from enum import Enum


IST_EMAIL_ADDRESS = 'enquires@invest-trade.uk'


class Template(Enum):
    """GOV.UK notifications template ids."""

    pm_requested = 'acbb9960-e1b4-465f-8aca-2a57fdfe2ad3'
    pm_rejected = 'b95b2c21-ab8e-4d10-a284-ea60361fdfd0'
