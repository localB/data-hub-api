from django.apps import AppConfig


class InvestmentConfig(AppConfig):
    """Configuration class for this app."""

    name = 'datahub.investment.projects'
    label = 'investment'

    def ready(self):
        """Registers the signals for this app.

        This is the preferred way to register signals in the Django documentation.
        """
        import datahub.investment.projects.signals  # noqa: F401
