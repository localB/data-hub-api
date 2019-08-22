from celery import shared_task
from notifications_python_client.errors import HTTPError

from datahub.notification.core import notify_gateway


@shared_task(
    bind=True,
    acks_late=True,
    priority=9,
)
def send_email_notification(
    self,
    recipient_email,
    template_identifier,
    context=None,
    notify_service_name=None,
):
    """
    Celery task to call the notify API to send a templated email notification
    to an email address.
    """
    try:
        response = notify_gateway.send_email_notification(
            recipient_email,
            template_identifier,
            context,
            notify_service_name,
        )
    except HTTPError as exc:
        # Raise 400/403 responses without retry
        if exc.status_code in (400, 403):
            raise exc
        raise self.retry(exc=exc, max_retries=5, countdown=60)
    return response['id']
