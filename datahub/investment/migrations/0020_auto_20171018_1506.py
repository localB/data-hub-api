# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-18 15:06
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('investment', '0019_add_assoc_r_and_d'),
    ]

    operations = [
        migrations.RenameField(
            model_name='investmentproject',
            old_name='address_line_1',
            new_name='address_1',
        ),
        migrations.RenameField(
            model_name='investmentproject',
            old_name='address_line_2',
            new_name='address_2',
        ),
        migrations.RenameField(
            model_name='investmentproject',
            old_name='address_line_3',
            new_name='address_postcode',
        ),
        migrations.RenameField(
            model_name='investmentproject',
            old_name='address_line_postcode',
            new_name='address_town',
        ),
    ]
