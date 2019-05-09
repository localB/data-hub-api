import io

import pytest
from django.conf import settings
from django.contrib import messages as django_messages
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.test import Client
from django.urls import reverse
from rest_framework import status

from datahub.company.test.factories import AdviserFactory
from datahub.core.test_utils import AdminTestMixin, create_test_user
from datahub.feature_flag.test.factories import FeatureFlagFactory
from datahub.interaction.admin_csv_import.views import INTERACTION_IMPORTER_FEATURE_FLAG_NAME
from datahub.interaction.models import Interaction, InteractionPermission
from datahub.interaction.test.admin_csv_import.utils import (
    make_csv_file,
    random_communication_channel,
    random_service,
)


@pytest.fixture()
def interaction_importer_feature_flag():
    """Creates the import interactions tool feature flag."""
    yield FeatureFlagFactory(code=INTERACTION_IMPORTER_FEATURE_FLAG_NAME)


import_interactions_url = reverse(
    admin_urlname(Interaction._meta, 'import'),
)
interaction_change_list_url = reverse(
    admin_urlname(Interaction._meta, 'changelist'),
)


class TestInteractionAdminChangeList(AdminTestMixin):
    """Tests for the contact admin change list."""

    @pytest.mark.usefixtures('interaction_importer_feature_flag')
    def test_load_import_link_exists(self):
        """
        Test that there is a link to import interactions on the interaction change list page.
        """
        response = self.client.get(interaction_change_list_url)
        assert response.status_code == status.HTTP_200_OK

        assert import_interactions_url in response.rendered_content

    def test_import_link_does_not_exist_if_only_has_view_permission(self):
        """
        Test that there is not a link to import interactions if the user only has the delete
        (but not change) permission for interactions.
        """
        user = create_test_user(
            permission_codenames=(InteractionPermission.view_all,),
            is_staff=True,
            password=self.PASSWORD,
        )

        client = self.create_client(user=user)
        response = client.get(interaction_change_list_url)
        assert response.status_code == status.HTTP_200_OK

        assert f'Select {Interaction._meta.verbose_name} to view' in response.rendered_content
        assert import_interactions_url not in response.rendered_content

    def test_import_link_does_not_exist_if_feature_flag_inactive(self):
        """
        Test that there is not a link to import interactions if the feature flag is inactive.
        """
        response = self.client.get(interaction_change_list_url)
        assert response.status_code == status.HTTP_200_OK

        assert import_interactions_url not in response.rendered_content


@pytest.mark.usefixtures('interaction_importer_feature_flag')
@pytest.mark.parametrize(
    'http_method,url',
    (
        ('get', import_interactions_url),
        ('post', import_interactions_url),
    ),
)
class TestAccessRestrictions(AdminTestMixin):
    """Tests permissions and other access restrictions on import interaction-related views."""

    def test_redirects_to_login_page_if_not_logged_in(self, http_method, url):
        """Test that the view redirects to the login page if the user isn't authenticated."""
        client = Client()
        # Note: Client.generic() doesn't support follow=True
        request_func = getattr(client, http_method)
        response = request_func(url, follow=True)

        assert response.status_code == status.HTTP_200_OK
        assert response.redirect_chain == [
            (self.login_url_with_redirect(url), status.HTTP_302_FOUND),
        ]

    def test_redirects_to_login_page_if_not_staff(self, url, http_method):
        """Test that the view redirects to the login page if the user isn't a member of staff."""
        user = create_test_user(is_staff=False, password=self.PASSWORD)

        client = self.create_client(user=user)
        # Note: Client.generic() doesn't support follow=True
        request_func = getattr(client, http_method)
        response = request_func(url, follow=True)

        assert response.status_code == status.HTTP_200_OK
        assert response.redirect_chain == [
            (self.login_url_with_redirect(url), status.HTTP_302_FOUND),
        ]

    def test_permission_denied_if_staff_and_without_change_permission(self, url, http_method):
        """
        Test that the view returns a 403 response if the staff user does not have the
        change interaction permission.
        """
        user = create_test_user(
            permission_codenames=(InteractionPermission.view_all,),
            is_staff=True,
            password=self.PASSWORD,
        )

        client = self.create_client(user=user)
        response = client.generic(http_method, url)
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    'http_method,url',
    (
        ('get', import_interactions_url),
        ('post', import_interactions_url),
    ),
)
class Test404IfFeatureFlagDisabled(AdminTestMixin):
    """
    Tests that import interaction-related views return a 404 if the feature flag is not
    active.

    (The feature flag not being active is implicit by it not being created,)
    """

    def test_returns_404_if_feature_flag_inactive(self, http_method, url):
        """Test that the a 404 is returned if the feature flag is inactive."""
        response = self.client.generic(
            http_method,
            url,
            data={},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.usefixtures('interaction_importer_feature_flag', 'local_memory_cache')
class TestImportInteractionsSelectFileView(AdminTestMixin):
    """Tests for the import interaction select file form."""

    def test_displays_page_if_with_correct_permissions(self):
        """
        Test that the view returns displays the form if the feature flag is active
        and the user has the correct permissions.
        """
        response = self.client.get(import_interactions_url)

        assert response.status_code == status.HTTP_200_OK
        assert 'form' in response.context

    def test_does_not_allow_file_without_correct_columns(self):
        """Test that the form rejects a CSV file that doesn't have the required columns."""
        file = make_csv_file(
            ('test',),
            ('row',),
        )

        response = self.client.post(
            import_interactions_url,
            data={
                'csv_file': file,
            },
        )

        assert response.status_code == status.HTTP_200_OK

        form = response.context['form']

        assert 'csv_file' in form.errors
        assert form.errors['csv_file'] == [
            'This file is missing the following required columns: '
            'adviser_1, contact_email, date, kind, service.',
        ]

    def test_rejects_large_files(self):
        """
        Test that large files are rejected.

        Note: INTERACTION_ADMIN_CSV_IMPORT_MAX_SIZE is set to 5 kB in config.settings.test
        """
        file_size = settings.INTERACTION_ADMIN_CSV_IMPORT_MAX_SIZE + 1
        file = io.BytesIO(b'-' * file_size)
        file.name = 'test.csv'

        response = self.client.post(
            import_interactions_url,
            data={
                'csv_file': file,
            },
        )

        assert response.status_code == status.HTTP_200_OK
        messages = list(response.context['messages'])
        assert len(messages) == 1
        assert messages[0].level == django_messages.ERROR
        assert messages[0].message == (
            'The file test.csv was too large. Files must be less than 5.0 KB.'
        )

    def test_redirects_on_valid_file(self):
        """Test that the user is redirected to the change list when a valid file is loaded."""
        adviser = AdviserFactory()
        service = random_service()
        communication_channel = random_communication_channel()
        file = make_csv_file(
            (
                'kind',
                'date',
                'adviser_1',
                'contact_email',
                'service',
                'communication_channel',
            ),
            (
                'interaction',
                '01/01/2018',
                adviser.name,
                'person@company.uk',
                service.name,
                communication_channel.name,
            ),
        )

        response = self.client.post(
            import_interactions_url,
            follow=True,
            data={
                'csv_file': file,
            },
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.redirect_chain == [
            (interaction_change_list_url, status.HTTP_302_FOUND),
        ]

    @pytest.mark.parametrize(
        'max_errors,should_be_truncated',
        (
            (5, True),
            (10, False),
        ),
    )
    def test_displays_errors_for_file_with_invalid_rows(
        self,
        max_errors,
        should_be_truncated,
        monkeypatch,
    ):
        """Test that errors are displayed for a file with invalid rows."""
        monkeypatch.setattr(
            'datahub.interaction.admin_csv_import.views.MAX_ERRORS_TO_DISPLAY',
            max_errors,
        )

        # This file should have 10 errors
        file = make_csv_file(
            ('kind', 'date', 'adviser_1', 'contact_email', 'service'),
            ('invalid', 'invalid', 'invalid', 'invalid', 'invalid'),
            ('invalid', 'invalid', 'invalid', 'invalid', 'invalid'),
        )

        response = self.client.post(
            import_interactions_url,
            data={
                'csv_file': file,
            },
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.context['errors']) == min(10, max_errors)
        assert response.context['are_errors_truncated'] == should_be_truncated
