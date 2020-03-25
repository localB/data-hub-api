import pytest
from django.urls import reverse
from rest_framework import status

from datahub.company.admin.adviser_forms import DUPLICATE_USER_MESSAGE
from datahub.company.admin.constants import ADMIN_ADD_ADVISER_FROM_SSO_FEATURE_FLAG
from datahub.company.models import Advisor
from datahub.company.test.factories import AdviserFactory
from datahub.core.test_utils import AdminTestMixin, create_test_user
from datahub.feature_flag.test.factories import FeatureFlagFactory

changelist_url = reverse('admin:company_advisor_changelist')
add_from_sso_url = reverse('admin:company_advisor_add-from-sso')


FAKE_SSO_USER_DATA = {
    'email': 'email@email.test',
    'user_id': 'c2c1afce-e45e-4139-9913-88b350f7a546',
    'email_user_id': 'test@id.test',
    'first_name': 'Johnny',
    'last_name': 'Cakeman',
    'related_emails': [],
    'contact_email': 'contact@email.test',
    'groups': [],
    'permitted_applications': [],
    'access_profiles': [],
}


class TestAdviserChangeListLinks(AdminTestMixin):
    """Tests for customisations for the adviser admin change list links."""

    @pytest.mark.parametrize(
        'permission_codenames,enable_feature_flag,should_link_exist',
        (
            (['view_advisor'], True, False),
            (['view_advisor', 'add_advisor'], True, True),
            (['view_advisor', 'add_advisor'], False, False),
        ),
    )
    def test_add_adviser_link_existence(
        self,
        permission_codenames,
        enable_feature_flag,
        should_link_exist,
    ):
        """
        Test that there is a link to add an adviser from SSO if the user has the correct
        permissions.
        """
        if enable_feature_flag:
            FeatureFlagFactory(code=ADMIN_ADD_ADVISER_FROM_SSO_FEATURE_FLAG)

        user = create_test_user(
            permission_codenames=permission_codenames,
            password=self.PASSWORD,
            is_staff=True,
        )

        client = self.create_client(user)
        response = client.get(changelist_url)
        assert response.status_code == status.HTTP_200_OK

        assert (add_from_sso_url in response.rendered_content) == should_link_exist


@pytest.mark.usefixtures('mock_get_user_by_email', 'mock_get_user_by_email_user_id')
class TestAddAdviserFromSSO(AdminTestMixin):
    """Tests for the add adviser from SSO view."""

    def test_displays_error_when_validation_fails(self, mock_get_user_by_email_user_id):
        """Test that an error is displayed when form validation fails."""
        mock_get_user_by_email_user_id.return_value = FAKE_SSO_USER_DATA
        AdviserFactory(sso_email_user_id=FAKE_SSO_USER_DATA['email_user_id'])

        data = {
            'search_email': FAKE_SSO_USER_DATA['email_user_id'],
        }

        response = self.client.post(add_from_sso_url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.context['errors'] == [[DUPLICATE_USER_MESSAGE]]

    def test_adds_a_new_adviser(self, mock_get_user_by_email_user_id):
        """Test that an adviser is created on success."""
        mock_get_user_by_email_user_id.return_value = FAKE_SSO_USER_DATA

        data = {
            'search_email': FAKE_SSO_USER_DATA['email_user_id'],
        }

        response = self.client.post(add_from_sso_url, data)

        assert response.status_code == status.HTTP_302_FOUND
        assert 'errors' not in response.context

        queryset = Advisor.objects.filter(sso_email_user_id=FAKE_SSO_USER_DATA['email_user_id'])
        assert queryset.exists()
