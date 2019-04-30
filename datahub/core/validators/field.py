from django.core.exceptions import ValidationError
from django.utils.timezone import now


def validate_date_is_in_the_future(date):
    if date < now().date():
        raise ValidationError('Date cannot be in the past')


def validate_date_is_in_the_past(date):
    if date > now().date():
        raise ValidationError('Date cannot be in the future')
