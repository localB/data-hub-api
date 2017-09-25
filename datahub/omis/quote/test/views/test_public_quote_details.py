import pytest

from django.utils.timezone import now
from freezegun import freeze_time
from oauth2_provider.models import Application
from rest_framework import status
from rest_framework.reverse import reverse

from datahub.core.test_utils import APITestMixin
from datahub.oauth.scopes import Scope
from datahub.omis.order.constants import OrderStatus
from datahub.omis.order.test.factories import OrderFactory, OrderWithOpenQuoteFactory

from ..factories import QuoteFactory


class TestPublicGetQuote(APITestMixin):
    """Get public quote test case."""

    @pytest.mark.parametrize(
        'order_status',
        (
            OrderStatus.quote_awaiting_acceptance,
            OrderStatus.quote_accepted,
            OrderStatus.paid,
            OrderStatus.complete
        )
    )
    def test_get(self, order_status):
        """Test a successful call to get a quote."""
        # in practice, accepted_on and cancelled_on will never be both set,
        # they are here just to check the response body
        order = OrderFactory(
            quote=QuoteFactory(
                accepted_on=now(),
                cancelled_on=now(),
            ),
            status=order_status
        )

        url = reverse(
            'api-v3:omis-public:quote:detail',
            kwargs={'public_token': order.public_token}
        )
        client = self.create_api_client(
            scope=Scope.public_omis_front_end,
            grant_type=Application.GRANT_CLIENT_CREDENTIALS
        )
        response = client.get(url, format='json')

        quote = order.quote
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            'created_on': quote.created_on.isoformat(),
            'cancelled_on': quote.cancelled_on.isoformat(),
            'accepted_on': quote.accepted_on.isoformat(),
            'expires_on': quote.expires_on.isoformat(),
            'content': quote.content
        }

    def test_404_if_order_doesnt_exist(self):
        """Test that if the order doesn't exist, the endpoint returns 404."""
        url = reverse(
            'api-v3:omis-public:quote:detail',
            kwargs={'public_token': ('1234-abcd-' * 5)}  # len(token) == 50
        )
        client = self.create_api_client(
            scope=Scope.public_omis_front_end,
            grant_type=Application.GRANT_CLIENT_CREDENTIALS
        )
        response = client.get(url, format='json')

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_404_if_quote_doesnt_exist(self):
        """Test that if the quote doesn't exist, the endpoint returns 404."""
        order = OrderFactory(status=OrderStatus.quote_awaiting_acceptance)
        assert not order.quote

        url = reverse(
            'api-v3:omis-public:quote:detail',
            kwargs={'public_token': order.public_token}
        )
        client = self.create_api_client(
            scope=Scope.public_omis_front_end,
            grant_type=Application.GRANT_CLIENT_CREDENTIALS
        )
        response = client.get(url, format='json')

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize(
        'order_status',
        (OrderStatus.draft, OrderStatus.cancelled)
    )
    def test_404_if_in_disallowed_status(self, order_status):
        """Test that if the order is not in an allowed state, the endpoint returns 404."""
        order = OrderFactory(status=order_status)

        url = reverse(
            'api-v3:omis-public:order:detail',
            kwargs={'public_token': order.public_token}
        )
        client = self.create_api_client(
            scope=Scope.public_omis_front_end,
            grant_type=Application.GRANT_CLIENT_CREDENTIALS
        )
        response = client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize('verb', ('post', 'patch', 'delete'))
    def test_verbs_not_allowed(self, verb):
        """Test that makes sure the other verbs are not allowed."""
        order = OrderFactory(
            quote=QuoteFactory(),
            status=OrderStatus.quote_awaiting_acceptance
        )

        url = reverse(
            'api-v3:omis-public:quote:detail',
            kwargs={'public_token': order.public_token}
        )
        client = self.create_api_client(
            scope=Scope.public_omis_front_end,
            grant_type=Application.GRANT_CLIENT_CREDENTIALS
        )
        response = getattr(client, verb)(url)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    @pytest.mark.parametrize(
        'scope',
        (s.value for s in Scope if s != Scope.public_omis_front_end.value)
    )
    def test_403_if_scope_not_allowed(self, scope):
        """Test that other oauth2 scopes are not allowed."""
        order = OrderFactory(
            quote=QuoteFactory(),
            status=OrderStatus.quote_awaiting_acceptance
        )

        url = reverse(
            'api-v3:omis-public:quote:detail',
            kwargs={'public_token': order.public_token}
        )
        client = self.create_api_client(
            scope=scope,
            grant_type=Application.GRANT_CLIENT_CREDENTIALS
        )
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestAcceptOrder(APITestMixin):
    """Tests for accepting a quote."""

    def test_404_if_order_doesnt_exist(self):
        """Test that if the order doesn't exist, the endpoint returns 404."""
        url = reverse(
            'api-v3:omis-public:quote:accept',
            kwargs={'public_token': ('1234-abcd-' * 5)}  # len(token) == 50
        )
        client = self.create_api_client(
            scope=Scope.public_omis_front_end,
            grant_type=Application.GRANT_CLIENT_CREDENTIALS
        )
        response = client.post(url, format='json')

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize(
        'disallowed_status',
        (
            OrderStatus.quote_accepted,
            OrderStatus.paid,
            OrderStatus.complete,
        )
    )
    def test_409_if_order_in_disallowed_status(self, disallowed_status):
        """
        Test that if the order is not in one of the allowed statuses, the endpoint
        returns 409.
        """
        quote = QuoteFactory()
        order = OrderFactory(
            status=disallowed_status,
            quote=quote
        )

        url = reverse(
            f'api-v3:omis-public:quote:accept',
            kwargs={'public_token': order.public_token}
        )
        client = self.create_api_client(
            scope=Scope.public_omis_front_end,
            grant_type=Application.GRANT_CLIENT_CREDENTIALS
        )
        response = client.post(url, format='json')

        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.json() == {
            'detail': (
                'The action cannot be performed '
                f'in the current status {OrderStatus[disallowed_status]}.'
            )
        }

    def test_accept(self):
        """Test that a quote can get accepted."""
        order = OrderWithOpenQuoteFactory()
        quote = order.quote

        url = reverse(
            f'api-v3:omis-public:quote:accept',
            kwargs={'public_token': order.public_token}
        )

        client = self.create_api_client(
            scope=Scope.public_omis_front_end,
            grant_type=Application.GRANT_CLIENT_CREDENTIALS
        )
        with freeze_time('2017-07-12 13:00') as mocked_now:
            response = client.post(url, format='json')

            assert response.status_code == status.HTTP_200_OK
            assert response.json() == {
                'created_on': quote.created_on.isoformat(),
                'accepted_on': mocked_now().isoformat(),
                'cancelled_on': None,
                'expires_on': quote.expires_on.isoformat(),
                'content': quote.content
            }

            quote.refresh_from_db()
            assert quote.is_accepted()
            assert quote.accepted_on == mocked_now()