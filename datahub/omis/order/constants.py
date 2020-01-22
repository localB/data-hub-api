from django.db import models
from model_utils import Choices


class OrderStatus(models.TextChoices):
    """Order statuses."""

    DRAFT = ('draft', 'Draft')
    QUOTE_AWAITING_ACCEPTANCE = (
        'quote_awaiting_acceptance',
        'Quote awaiting acceptance',
    )
    QUOTE_ACCEPTED = ('quote_accepted', 'Quote accepted')
    PAID = ('paid', 'Paid')
    COMPLETE = ('complete', 'Complete')
    CANCELLED = ('cancelled', 'Cancelled')


DEFAULT_HOURLY_RATE = '7e1ca5c3-dc5a-e511-9d3c-e4115bead28a'


VATStatus = Choices(
    ('uk', 'UK'),
    ('eu', 'EU excluding the UK'),
    ('outside_eu', 'Outside the EU'),
)
