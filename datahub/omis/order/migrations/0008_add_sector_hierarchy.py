# Generated by Django 2.0.3 on 2018-03-12 11:05

from django.db import migrations
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0007_populate_uk_region'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='sector',
            field=mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='metadata.Sector'),
        ),
    ]
