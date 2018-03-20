# Generated by Django 2.0.2 on 2018-03-20 15:34

from pathlib import PurePath

from django.core.management import call_command
from django.db import migrations


def load_initial_statuses(apps, schema_editor):
    call_command(
        'loaddata',
        PurePath(__file__).parent / '0003_add_additional_services.yaml'
    )


class Migration(migrations.Migration):

    dependencies = [
        ('metadata', '0002_add_sector_hierarchy'),
    ]

    operations = [
        migrations.RunPython(load_initial_statuses, migrations.RunPython.noop)
    ]
