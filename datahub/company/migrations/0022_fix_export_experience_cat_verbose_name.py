# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-30 16:08
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0021_add_default_id_for_metadata'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='exportexperiencecategory',
            options={'ordering': ('name',), 'verbose_name_plural': 'export experience categories'},
        ),
    ]
