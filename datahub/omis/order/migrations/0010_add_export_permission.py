# Generated by Django 2.1 on 2018-08-30 13:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0009_update_permissions_django_21'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'permissions': (('export_order', 'Can export order'),)},
        ),
    ]