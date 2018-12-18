# Generated by Django 2.1.3 on 2018-11-27 10:45

import django.core.validators
from django.db import migrations, models
import re


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0043_update_one_list_core_team_member_rels'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='duns_number',
            field=models.CharField(blank=True, null=True, default='', help_text='Dun & Bradstreet unique identifier. Nine-digit number with leading zeros.', max_length=9, validators=[django.core.validators.MinLengthValidator(9), django.core.validators.MaxLengthValidator(9), django.core.validators.RegexValidator(re.compile('^-?\\d+\\Z'), code='invalid', message='Enter a valid integer.')]),
        ),
    ]