from unittest import mock

import pytest
from dateutil.parser import parse as dateutil_parse

from datahub.omis.order.constants import OrderStatus
from datahub.omis.order.test.factories import OrderWithAcceptedQuoteFactory
from .factories import PaymentGatewaySessionFactory
from ..constants import PaymentGatewaySessionStatus, PaymentMethod
from ..govukpay import govuk_url, GOVUKPayAPIException
from ..models import Payment, PaymentGatewaySession


class TestPaymentGatewaySessionIsFinished:
    """Tests for the `is_finished` method."""

    @pytest.mark.parametrize(
        'status,finished',
        (
            (PaymentGatewaySessionStatus.created, False),
            (PaymentGatewaySessionStatus.started, False),
            (PaymentGatewaySessionStatus.submitted, False),
            (PaymentGatewaySessionStatus.success, True),
            (PaymentGatewaySessionStatus.failed, True),
            (PaymentGatewaySessionStatus.cancelled, True),
            (PaymentGatewaySessionStatus.error, True),
        )
    )
    def test_value(self, status, finished):
        """
        Test the return value of `is_finished` with different values of session.status.
        """
        session = PaymentGatewaySession(status=status)
        assert session.is_finished() == finished


@pytest.mark.django_db
class TestPaymentGatewaySessionRefresh:
    """Tests for the `refresh_from_govuk_payment` method."""

    @pytest.mark.parametrize(
        'status', (
            PaymentGatewaySessionStatus.success,
            PaymentGatewaySessionStatus.failed,
            PaymentGatewaySessionStatus.cancelled,
            PaymentGatewaySessionStatus.error,
        )
    )
    def test_already_finished_doesnt_do_anything(self, status, requests_stubber):
        """
        Test that if the payment gateway session is already finished, the system
        doesn't call GOV.UK Pay as it's already in its end state.
        """
        session = PaymentGatewaySession(status=status)

        assert not session.refresh_from_govuk_payment()
        assert not requests_stubber.called

    @pytest.mark.parametrize(
        'status',
        (
            PaymentGatewaySessionStatus.created,
            PaymentGatewaySessionStatus.started,
            PaymentGatewaySessionStatus.submitted,
        )
    )
    def test_with_unchanged_govuk_payment_status_doesnt_change_anything(
        self, status, requests_stubber
    ):
        """
        Test that if the GOV.UK payment status is the same as the payment gateway session one,
        (meaning that the payment gateway session is up-to-date), the record is not changed.
        """
        session = PaymentGatewaySession(status=status)
        url = govuk_url(f'payments/{session.govuk_payment_id}')
        requests_stubber.get(
            url, status_code=200, json={
                'state': {'status': status, 'finished': False}
            }
        )

        assert not session.refresh_from_govuk_payment()
        assert session.status == status
        assert Payment.objects.count() == 0

        assert requests_stubber.call_count == 1

    @pytest.mark.parametrize(
        'status',
        (
            status[0] for status in PaymentGatewaySessionStatus
            if status[0] != PaymentGatewaySessionStatus.success
        )
    )
    def test_with_different_govuk_payment_status_updates_session(self, status, requests_stubber):
        """
        Test that if the GOV.UK payment status is not the same as the payment gateway session one,
        the record is updated.
        """
        # choose an initial status != from the govuk one to test the update
        initial_status = PaymentGatewaySessionStatus.created
        if initial_status == status:
            initial_status = PaymentGatewaySessionStatus.started

        session = PaymentGatewaySessionFactory(status=initial_status)
        url = govuk_url(f'payments/{session.govuk_payment_id}')
        requests_stubber.get(
            url, status_code=200, json={
                'state': {'status': status}
            }
        )

        assert session.refresh_from_govuk_payment()

        session.refresh_from_db()
        assert session.status == status

        assert requests_stubber.call_count == 1

    def test_with_govuk_payment_success_updates_order(self, requests_stubber):
        """
        Test that if the GOV.UK payment status is `success` and the payment gateway session is
        out of date, the record is updated, the related order marked as `paid` and an OMIS
        `payment.Payment` record created from the GOV.UK response data one.
        """
        order = OrderWithAcceptedQuoteFactory()
        session = PaymentGatewaySessionFactory(
            status=PaymentGatewaySessionStatus.created,
            order=order
        )
        url = govuk_url(f'payments/{session.govuk_payment_id}')
        response_json = {
            'amount': order.total_cost,
            'state': {'status': 'success'},
            'email': 'email@example.com',
            'created_date': '2018-02-13T14:56:56.734Z',
            'card_details': {
                'last_digits_card_number': '1111',
                'cardholder_name': 'John Doe',
                'expiry_date': '01/20',
                'billing_address': {
                    'line1': 'line 1 address',
                    'line2': 'line 2 address',
                    'postcode': 'SW1A 1AA',
                    'city': 'London',
                    'country': 'GB'
                },
                'card_brand': 'Visa',
            },
        }
        requests_stubber.get(url, status_code=200, json=response_json)

        assert session.refresh_from_govuk_payment()

        # check session
        session.refresh_from_db()
        assert session.status == PaymentGatewaySessionStatus.success

        # checko order
        order.refresh_from_db()
        assert order.status == OrderStatus.paid

        # check payment object
        assert Payment.objects.filter(order=order).count() == 1

        payment = Payment.objects.filter(order=order).first()
        assert payment.amount == response_json['amount']
        assert payment.method == PaymentMethod.card
        assert payment.received_on == dateutil_parse('2018-02-13').date()

        assert payment.cardholder_name == 'John Doe'
        assert payment.card_brand == 'Visa'
        assert payment.billing_email == 'email@example.com'
        assert payment.billing_address_1 == 'line 1 address'
        assert payment.billing_address_2 == 'line 2 address'
        assert payment.billing_address_town == 'London'
        assert payment.billing_address_postcode == 'SW1A 1AA'
        assert payment.billing_address_country == 'GB'

        assert requests_stubber.call_count == 1

    def test_atomicity_when_govuk_pay_errors(self, requests_stubber):
        """
        Test that if GOV.UK Pay errors, none of the changes persists.
        """
        session = PaymentGatewaySessionFactory()
        original_session_status = session.status

        url = govuk_url(f'payments/{session.govuk_payment_id}')
        requests_stubber.get(url, status_code=500)

        with pytest.raises(GOVUKPayAPIException):
            assert session.refresh_from_govuk_payment()

        session.refresh_from_db()
        assert session.status == original_session_status

        assert requests_stubber.call_count == 1

    def test_atomicity_when_session_save_errors(self, requests_stubber):
        """
        Test that if the PaymentGatewaySession.save() call fails, none of the changes persists.
        """
        session = PaymentGatewaySessionFactory()
        original_session_status = session.status
        url = govuk_url(f'payments/{session.govuk_payment_id}')
        requests_stubber.get(
            url, status_code=200, json={
                'state': {'status': 'success'}
            }
        )
        session.save = mock.MagicMock(side_effect=Exception())

        with pytest.raises(Exception):
            session.refresh_from_govuk_payment()

        session.refresh_from_db()
        assert session.status == original_session_status

        assert requests_stubber.call_count == 1

    def test_atomicity_when_order_save_errors(self, requests_stubber):
        """
        Test that if the order.mark_as_paid() call fails, non of the changes persists.
        """
        session = PaymentGatewaySessionFactory()
        original_session_status = session.status
        url = govuk_url(f'payments/{session.govuk_payment_id}')
        requests_stubber.get(
            url, status_code=200, json={
                'state': {'status': 'success'}
            }
        )
        session.order.mark_as_paid = mock.MagicMock(side_effect=Exception())

        with pytest.raises(Exception):
            session.refresh_from_govuk_payment()

        session.refresh_from_db()
        assert session.status == original_session_status

        assert requests_stubber.call_count == 1


@pytest.mark.django_db
class TestPaymentGatewaySessionCancel:
    """Tests for the `cancel` method."""

    def test_cancel_updates_session(self, requests_stubber):
        """
        Test that if GOV.UK Pay cancels and acknowledges the change,
        the session object is updated.
        """
        session = PaymentGatewaySessionFactory()
        requests_stubber.post(
            govuk_url(f'payments/{session.govuk_payment_id}/cancel'),
            status_code=204
        )
        requests_stubber.get(
            govuk_url(f'payments/{session.govuk_payment_id}'),
            status_code=200,
            json={'state': {'status': 'cancelled'}}
        )

        session.cancel()

        session.refresh_from_db()
        assert session.status == PaymentGatewaySessionStatus.cancelled

        assert requests_stubber.call_count == 2

    def test_with_govuk_pay_erroring_when_cancelling(self, requests_stubber):
        """
        Test that if GOV.UK Pay errors when cancelling the payment,
        the session object is not updated.
        """
        session = PaymentGatewaySessionFactory()
        original_session_status = session.status
        requests_stubber.post(
            govuk_url(f'payments/{session.govuk_payment_id}/cancel'),
            status_code=500
        )

        with pytest.raises(GOVUKPayAPIException):
            session.cancel()

        session.refresh_from_db()
        assert session.status == original_session_status

        assert requests_stubber.call_count == 1

    def test_with_govuk_pay_erroring_when_refreshing(self, requests_stubber):
        """
        Test that if GOV.UK Pay cancels the payment but errors when
        refreshing the session, the session object is not updated
        (but the GOV.UK payment is still cancelled).
        This is okay as the session object will get refreshed at the next
        opportunity.
        """
        session = PaymentGatewaySessionFactory()
        original_session_status = session.status
        requests_stubber.post(
            govuk_url(f'payments/{session.govuk_payment_id}/cancel'),
            status_code=204
        )
        requests_stubber.get(
            govuk_url(f'payments/{session.govuk_payment_id}'),
            status_code=500
        )

        with pytest.raises(GOVUKPayAPIException):
            session.cancel()

        session.refresh_from_db()
        assert session.status == original_session_status

        assert requests_stubber.call_count == 2