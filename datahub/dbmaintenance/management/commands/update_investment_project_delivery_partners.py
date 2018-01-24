from logging import getLogger

import reversion

from datahub.dbmaintenance.utils import parse_uuid, parse_uuid_list
from datahub.investment.models import InvestmentProject
from ..base import CSVBaseCommand


logger = getLogger(__name__)


class Command(CSVBaseCommand):
    """Command to update InvestmentProject.delivery_partners."""

    def add_arguments(self, parser):
        """Define extra arguments."""
        super().add_arguments(parser)
        parser.add_argument(
            '--simulate',
            action='store_true',
            dest='simulate',
            default=False,
            help='If True it only simulates the command without saving the changes.',
        )

    def _process_row(self, row, simulate=False, **options):
        """Process one single row."""
        pk = parse_uuid(row['id'])
        investment_project = InvestmentProject.objects.get(pk=pk)
        new_delivery_partners = parse_uuid_list(row['delivery_partners'])

        if investment_project.delivery_partners.all():
            logger.warning('Not updating project with existing delivery partners: %s, %s',
                           investment_project.project_code, investment_project)
            return

        if not simulate:
            with reversion.create_revision():
                investment_project.delivery_partners.set(new_delivery_partners)
                reversion.set_comment('Investment delivery partners migration.')