# Generated by Django 3.0.3 on 2020-02-27 13:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('interaction', '0070_add_interaction_export_countries'),
        ('company_referral', '0003_add_interaction_field'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companyreferral',
            name='interaction',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='company_referral', to='interaction.Interaction'),
        ),
    ]
