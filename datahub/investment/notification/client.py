from logging import getLogger

from django.conf import settings
from notifications_python_client.notifications import NotificationsAPIClient

from datahub.core.thread_pool import submit_to_thread_pool
from datahub.investment.notification.constants import Template, IST_EMAIL_ADDRESS


logger = getLogger(__name__)


def send_email(client, **kwargs):
    """Send email and catch potential errors."""
    data = dict(kwargs)
    client.send_email_notification(**data)


class Notify:
    """
    Used to send notifications about investment projects.

    The GOV.UK notification key can be set in settings.INVESTMENTS_NOTIFICATION_API_KEY:
    if empty, the client will be mocked and no notification will be sent.

    """

    def __init__(self):
        """Init underlying notification client."""

        if settings.INVESTMENTS_NOTIFICATION_API_KEY:
            self.client = NotificationsAPIClient(
                settings.INVESTMENTS_NOTIFICATION_API_KEY,
            )
        else:
            self.client = None

    def _send_email(self, **kwargs):
        """Send email in a separate thread."""
        submit_to_thread_pool(send_email, self.client, **kwargs)

    def project_manager_requested(self, investment_project):
        """
        Send a notification to IST that a project manager has been requested.
        """
        self._send_email(
            email_address=IST_EMAIL_ADDRESS,
            template_id=Template.pm_requested.value,
            personalisation={
                'name': investment_project.name,
                'region': investment_project.investor_company_country.overseas_region.name,
                'link': investment_project.get_absolute_url(),
            },
        )

    def project_manager_rejected(self, investment_project):
        """
        Send a notification to the POST that a request for a project manager has been rejected.
        """
        self._send_email(
            email_address=investment_project.created_by.email,
            template_id=Template.pm_rejected.value,
            personalisation={
                'name': investment_project.name,
                'link': investment_project.get_absolute_url(),
                'note': '',
                'show_note': 'yes' if investment_project.note else 'no'
            },
        )


notify = Notify()
