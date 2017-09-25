import pytest

from oauth2_provider.models import Application
from rest_framework import status
from rest_framework.reverse import reverse

from datahub.core.test_utils import APITestMixin
from datahub.oauth.scopes import Scope
from datahub.omis.quote.test.factories import QuoteFactory

from ..factories import OrderFactory
from ...constants import OrderStatus


# mark the whole module for db use
pytestmark = pytest.mark.django_db


class TestViewPublicOrderDetails(APITestMixin):
    """Tests for the pubic facing order endpoints."""

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
        """Test getting an existing order by `public_token`."""
        order = OrderFactory(
            quote=QuoteFactory(),
            status=order_status
        )

        url = reverse(
            'api-v3:omis-public:order:detail',
            kwargs={'public_token': order.public_token}
        )
        client = self.create_api_client(
            scope=Scope.public_omis_front_end,
            grant_type=Application.GRANT_CLIENT_CREDENTIALS
        )
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            'public_token': order.public_token,
            'reference': order.reference,
            'status': order.status,
            'created_on': order.created_on.isoformat(),
            'company': {
                'id': str(order.company.pk),
                'name': order.company.name,
                'registered_address_1': order.company.registered_address_1,
                'registered_address_2': order.company.registered_address_2,
                'registered_address_county': order.company.registered_address_county,
                'registered_address_postcode': order.company.registered_address_postcode,
                'registered_address_town': order.company.registered_address_town,
                'registered_address_country': {
                    'id': str(order.company.registered_address_country.pk),
                    'name': order.company.registered_address_country.name
                },
            },
            'contact': {
                'id': str(order.contact.pk),
                'name': order.contact.name
            },
            'contact_email': order.contact_email,
            'contact_phone': order.contact_phone,
            'po_number': order.po_number,
            'discount_value': order.discount_value,
            'net_cost': order.net_cost,
            'subtotal_cost': order.subtotal_cost,
            'vat_cost': order.vat_cost,
            'total_cost': order.total_cost,
            'billing_contact_name': order.billing_contact_name,
            'billing_email': order.billing_email,
            'billing_phone': order.billing_phone,
            'billing_address_1': order.billing_address_1,
            'billing_address_2': order.billing_address_2,
            'billing_address_town': order.billing_address_town,
            'billing_address_county': order.billing_address_county,
            'billing_address_postcode': order.billing_address_postcode,
            'billing_address_country': {
                'id': str(order.billing_address_country.pk),
                'name': order.billing_address_country.name
            },
        }

    def test_not_found_with_invalid_public_token(self):
        """Test 404 when getting a non-existent order."""
        url = reverse(
            'api-v3:omis-public:order:detail',
            kwargs={'public_token': ('1234-abcd-' * 5)}  # len(token) == 50
        )
        client = self.create_api_client(
            scope=Scope.public_omis_front_end,
            grant_type=Application.GRANT_CLIENT_CREDENTIALS
        )
        response = client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize(
        'order_status',
        (OrderStatus.draft, OrderStatus.cancelled)
    )
    def test_not_found_if_in_disallowed_status(self, order_status):
        """Test 404 when the order is not in an allowed state."""
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
            'api-v3:omis-public:order:detail',
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
    def test_other_scopes_not_allowed(self, scope):
        """Test that other oauth2 scopes are not allowed."""
        order = OrderFactory(
            quote=QuoteFactory(),
            status=OrderStatus.quote_awaiting_acceptance
        )

        url = reverse(
            'api-v3:omis-public:order:detail',
            kwargs={'public_token': order.public_token}
        )
        client = self.create_api_client(
            scope=scope,
            grant_type=Application.GRANT_CLIENT_CREDENTIALS
        )
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN