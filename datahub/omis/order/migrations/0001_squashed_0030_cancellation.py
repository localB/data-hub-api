# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-26 13:33
from __future__ import unicode_literals

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


def create_default_hourlyrate(apps, schema_editor):
    HourlyRate = apps.get_model('order', 'HourlyRate')
    HourlyRate.objects.get_or_create(
        id='7e1ca5c3-dc5a-e511-9d3c-e4115bead28a',
        defaults={
            'name': 'Default rate',
            'rate_value': 1000,
            'vat_value': '20.00'
        }
    )


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('metadata', '0002_rename_phase_to_stage'),
        ('omis-invoice', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('omis-quote', '0001_initial'),
        ('company', '0001_squashed_0010_auto_20170807_1124'),
        ('metadata', '0004_team_roles_regions_countries'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('created_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified_on', models.DateTimeField(auto_now=True, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('reference', models.CharField(max_length=100)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='orders', to='company.Company')),
                ('contact', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='orders', to='company.Contact')),
                ('primary_market', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='metadata.Country')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OrderSubscriber',
            fields=[
                ('created_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified_on', models.DateTimeField(auto_now=True, null=True)),
                ('id', models.UUIDField(db_index=True, default=uuid.uuid4, primary_key=True, serialize=False)),
                ('adviser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscribers', to='order.Order')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='ordersubscriber',
            unique_together=set([('order', 'adviser')]),
        ),
        migrations.AlterModelOptions(
            name='ordersubscriber',
            options={'ordering': ['created_on']},
        ),
        migrations.AlterField(
            model_name='ordersubscriber',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False),
        ),
        migrations.AddField(
            model_name='order',
            name='sector',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='metadata.Sector'),
        ),
        migrations.AddField(
            model_name='order',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='order',
            name='modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='ordersubscriber',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='ordersubscriber',
            name='modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='OrderAssignee',
            fields=[
                ('created_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified_on', models.DateTimeField(auto_now=True, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('estimated_time', models.IntegerField(default=0, help_text='Estimated time in minutes.', validators=[django.core.validators.MinValueValidator(0)])),
                ('is_lead', models.BooleanField(default=False)),
                ('adviser', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('country', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='metadata.Country')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignees', to='order.Order')),
                ('team', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='metadata.Team')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='orderassignee',
            unique_together=set([('order', 'adviser')]),
        ),
        migrations.AlterModelOptions(
            name='orderassignee',
            options={'ordering': ['created_on']},
        ),
        migrations.AlterField(
            model_name='order',
            name='created_on',
            field=models.DateTimeField(auto_now_add=True, db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='orderassignee',
            name='created_on',
            field=models.DateTimeField(auto_now_add=True, db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='ordersubscriber',
            name='created_on',
            field=models.DateTimeField(auto_now_add=True, db_index=True, null=True),
        ),
        migrations.CreateModel(
            name='ServiceType',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('name', models.TextField(blank=True)),
                ('order', models.FloatField(default=0.0)),
                ('disabled_on', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'ordering': ('order',),
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='order',
            name='service_types',
            field=models.ManyToManyField(blank=True, related_name='orders', to='order.ServiceType'),
        ),
        migrations.AddField(
            model_name='order',
            name='contacts_not_to_approach',
            field=models.TextField(blank=True, help_text='Specific people or organisations the company does not want DIT to talk to.'),
        ),
        migrations.AddField(
            model_name='order',
            name='description',
            field=models.TextField(blank=True, help_text='Description of the work needed.'),
        ),
        migrations.AddField(
            model_name='order',
            name='existing_agents',
            field=models.TextField(blank=True, help_text='Contacts the company already has in the market.'),
        ),
        migrations.AddField(
            model_name='order',
            name='further_info',
            field=models.TextField(blank=True, help_text='Additional notes and useful information.'),
        ),
        migrations.AddField(
            model_name='order',
            name='permission_to_approach_contacts',
            field=models.TextField(blank=True, editable=False, help_text='Legacy field. Can DIT speak to the contacts?'),
        ),
        migrations.AddField(
            model_name='order',
            name='product_info',
            field=models.TextField(blank=True, editable=False, help_text='Legacy field. What is the product?'),
        ),
        migrations.AddField(
            model_name='order',
            name='delivery_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='contact_email',
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name='order',
            name='contact_phone',
            field=models.CharField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name='order',
            name='quote',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='omis-quote.Quote'),
        ),
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('draft', 'Draft'), ('quote_awaiting_acceptance', 'Quote awaiting acceptance'), ('quote_accepted', 'Quote accepted'), ('paid', 'Paid'), ('complete', 'Complete'), ('cancelled', 'Cancelled')], default='draft', max_length=100),
        ),
        migrations.AddField(
            model_name='order',
            name='po_number',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.CreateModel(
            name='HourlyRate',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('name', models.TextField(blank=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('modified_on', models.DateTimeField(auto_now=True)),
                ('rate_value', models.PositiveIntegerField(help_text='Rate in pence. E.g. 1 pound should be stored as 100 (100 pence).')),
                ('vat_value', models.DecimalField(decimal_places=2, help_text='VAT to apply as percentage value (0.00 to 100.00).', max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
            ],
            options={
                'ordering': ('name',),
                'abstract': False,
                'db_table': 'omis-order_hourlyrate',
            },
        ),
        migrations.RunPython(
            code=create_default_hourlyrate,
            reverse_code=migrations.RunPython.noop
        ),
        migrations.AddField(
            model_name='order',
            name='hourly_rate',
            field=models.ForeignKey(default='7e1ca5c3-dc5a-e511-9d3c-e4115bead28a', on_delete=django.db.models.deletion.PROTECT, related_name='orders', to='order.HourlyRate'),
        ),
        migrations.AddField(
            model_name='order',
            name='discount_label',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='order',
            name='discount_value',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='order',
            name='vat_number',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='order',
            name='vat_status',
            field=models.CharField(blank=True, choices=[('uk', 'UK'), ('eu', 'EU excluding the UK'), ('outside_eu', 'Outside the EU')], max_length=100),
        ),
        migrations.AddField(
            model_name='order',
            name='vat_verified',
            field=models.NullBooleanField(),
        ),
        migrations.AddField(
            model_name='order',
            name='net_cost',
            field=models.PositiveIntegerField(default=0, help_text='Total hours * hourly rate in pence.'),
        ),
        migrations.AddField(
            model_name='order',
            name='subtotal_cost',
            field=models.PositiveIntegerField(default=0, help_text='Net cost - discount value in pence.'),
        ),
        migrations.AddField(
            model_name='order',
            name='total_cost',
            field=models.PositiveIntegerField(default=0, help_text='Subtotal + VAT cost in pence.'),
        ),
        migrations.AddField(
            model_name='order',
            name='vat_cost',
            field=models.PositiveIntegerField(default=0, help_text='VAT amount of subtotal in pence.'),
        ),
        migrations.AddField(
            model_name='order',
            name='public_token',
            field=models.CharField(blank=True, help_text='Used for public facing access.', max_length=100),
        ),
        migrations.AlterField(
            model_name='order',
            name='public_token',
            field=models.CharField(help_text='Used for public facing access.', max_length=100, unique=True),
        ),
        migrations.AddField(
            model_name='order',
            name='billing_address_1',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='order',
            name='billing_address_2',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='order',
            name='billing_address_country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='metadata.Country'),
        ),
        migrations.AddField(
            model_name='order',
            name='billing_address_county',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='order',
            name='billing_address_postcode',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='order',
            name='billing_address_town',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='order',
            name='billing_contact_name',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='order',
            name='billing_email',
            field=models.EmailField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='order',
            name='billing_phone',
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AddField(
            model_name='order',
            name='invoice',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='omis-invoice.Invoice'),
        ),
        migrations.AddField(
            model_name='hourlyrate',
            name='disabled_on',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='archived_documents_url_path',
            field=models.CharField(blank=True, help_text='Legacy field. Link to the archived documents for this order.', max_length=255),
        ),
        migrations.AddField(
            model_name='order',
            name='completed_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='order',
            name='completed_on',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='orderassignee',
            name='actual_time',
            field=models.IntegerField(blank=True, help_text='Actual time in minutes.', null=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.CreateModel(
            name='CancellationReason',
            fields=[
                ('disabled_on', models.DateTimeField(blank=True, null=True)),
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('name', models.TextField(blank=True)),
                ('order', models.FloatField(default=0.0)),
            ],
            options={
                'ordering': ('order',),
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='order',
            name='cancelled_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='order',
            name='cancelled_on',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='cancellation_reason',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='order.CancellationReason'),
        ),
    ]
