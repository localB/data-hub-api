import uuid

from rest_framework import status
from rest_framework.reverse import reverse

from datahub.core.test_utils import APITestMixin, create_test_user


class TestCreateLargeCapitalUKOpportunityView(APITestMixin):
    """Test creating a large capital uk opportunity"""

    def test_large_capital_unauthorized_user(self, api_client):
        """Should return 401"""
        url = reverse('api-v4:large-capital-uk-opportunity:collection')
        user = create_test_user()
        response = api_client.get(url, user=user)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_large_capital_uk_opportunity_fail(self):
        """Test creating a large capital uk opportunity without an opportunity name."""
        url = reverse('api-v4:large-capital-uk-opportunity:collection')
        request_data = {}
        response = self.api_client.post(url, data=request_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_data = response.json()
        assert response_data == {
            'opportunity_name': ['This field is required.'],
        }

    def test_create_large_capital_uk_opportunity(self):
        """Test creating a large capital uk opportunity."""
        url = reverse('api-v4:large-capital-uk-opportunity:collection')
        request_data = {'opportunity_name': 'hello'}
        response = self.api_client.post(url, data=request_data)
        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data == {}

    def test_create_large_capital_uk_opportunity_status(self):
        """Test creating a large capital uk opportunity."""
        url = reverse('api-v4:large-capital-uk-opportunity:collection')
        request_data = {
            'opportunity_name': 'hello',
            'status_detail': {
                'status': {'id': uuid.UUID('fa2d3c77-66db-42ed-98e4-af974fe83986')},
            },
        }
        response = self.api_client.post(url, data=request_data)
        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data == {}
