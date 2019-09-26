# Generated by Django 2.2.4 on 2019-09-19 10:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interaction', '0067_remove_interaction_location_from_django'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddField(
                    model_name='interaction',
                    name='location',
                    field=models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                    )
                ),
            ],
        ),
        migrations.RemoveField(
            model_name='interaction',
            name='location',
        ),
    ]
