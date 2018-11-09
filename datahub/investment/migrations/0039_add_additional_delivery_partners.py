# Generated by Django 2.0.1 on 2018-01-23 11:40

from pathlib import PurePath

from django.core.management import call_command
from django.db import migrations
<<<<<<< HEAD


def load_delivery_partners(apps, schema_editor):
    call_command(
        'loaddata',
=======
from datahub.core.migration_utils import load_yaml_data_in_migration


def load_delivery_partners(apps, schema_editor):
    load_yaml_data_in_migration(
        apps,
>>>>>>> d7a9b640... Add extra tests
        PurePath(__file__).parent / '0039_additional_delivery_partners.yaml'
    )


class Migration(migrations.Migration):

    dependencies = [
        ('investment', '0038_correct_site_decided'),
    ]

    operations = [
        migrations.RunPython(load_delivery_partners, migrations.RunPython.noop)
    ]
