import codecs
import csv
from contextlib import closing
from logging import getLogger
from django.core.management.base import BaseCommand

from datahub.core.utils import get_s3_client


logger = getLogger(__name__)


class CSVBaseCommand(BaseCommand):
    """
    Base class for db maintenance related commands.
    It helps dealing with processing rows in a CSV stored in S3,
    manages basic logging and failures.
    The operation is not atomic and each row is processed individually.

    Usage:
        class Command(CSVBaseCommand):
            def _process_row(self, row, **options):
                # process row['col1'], row['col2'] where col1, col2 are the
                # values in the header
                ...

        ./manage.py <command-name> <bucket> <object_key>
    """

    def add_arguments(self, parser):
        """Define extra arguments."""
        parser.add_argument('bucket', help='S3 bucket where the CSV is stored.')
        parser.add_argument('object_key', help='S3 key of the CSV file.')

    def handle(self, *args, **options):
        """Process the CSV file."""
        result = {True: 0, False: 0}

        logger.info(f'Started')

        s3_client = get_s3_client()
        response = s3_client.get_object(
            Bucket=options['bucket'],
            Key=options['object_key']
        )['Body']

        with closing(response):
            csvfile = codecs.getreader('utf-8')(response)
            reader = csv.DictReader(csvfile)

            for row in reader:
                succeeded = self.process_row(row, **options)
                result[succeeded] += 1

        logger.info(f'Finished - succeeded: {result[True]}, failed: {result[False]}')

    def process_row(self, row, **options):
        """
        Process one single row.

        :returns: True if the row has been processed successfully, False otherwise.
        """
        try:
            self._process_row(row, **options)
        except Exception as e:
            logger.exception(f'Row {row} - Failed')
            return False
        else:
            logger.info(f'Row {row} - OK')
            return True

    def _process_row(self, row, **options):
        """
        To be implemented by a subclass, it should propagate exceptions so that `process_row` knows
        that the row has not been successfully processed.

        :param row: dict where the keys are defined in the header and the values are the CSV row
        :param options: same as the django command options
        """
        raise NotImplementedError()