import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from datahub.core.models import (
    BaseModel,
    BaseOrderedConstantModel,
)
from datahub.core.validators.field import validate_date_is_in_the_past


class LargeCapitalUKOpportunityPromoter(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
    )

    opportunity = models.ForeignKey(
        'uk_opportunity.LargeCapitalUKOpportunity',
        related_name='promoters',
        on_delete=models.CASCADE,
    )

    company = models.ForeignKey(
        'company.Company',
        related_name='uk_opportunity_promoters',
        on_delete=models.CASCADE,
    )

    key_client_contact = models.ForeignKey(
        'company.Contact',
        related_name='uk_opportunity_promoters',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )


class LargeCapitalUKOpportunity(BaseModel):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
    )

    required_checks_conducted = models.ForeignKey(
        'investor_profile.RequiredChecksConducted',
        related_name='+',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    required_checks_conducted_by = models.ForeignKey(
        'company.Advisor',
        related_name='+',
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )

    required_checks_conducted_on = models.DateField(
        null=True,
        blank=True,
        validators=[validate_date_is_in_the_past],
    )

    opportunity_name = models.CharField(max_length=80)

    opportunity_description = models.TextField(blank=True, default='')

    asset_classes_of_interest = models.ManyToManyField(
        'investor_profile.AssetClassInterest',
        related_name='+',
        blank=True,
    )

    construction_risks = models.ManyToManyField(
        'investor_profile.ConstructionRisk',
        related_name='+',
        blank=True,
    )

    uk_region_locations = models.ManyToManyField(
        'metadata.UKRegion',
        related_name='+',
        blank=True,
        verbose_name='possible UK regions',
    )

    estimated_return_rate = models.ForeignKey(
        'investor_profile.ReturnRate',
        related_name='+',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    time_scales = models.ForeignKey(
        'investor_profile.TimeHorizon',
        related_name='+',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    investment_types = models.ManyToManyField(
        'investor_profile.LargeCapitalInvestmentType',
        related_name='+',
        blank=True,
    )

    total_investment_sought = models.BigIntegerField(
        null=True,
        blank=True,
        help_text='Total investment sought amount in GBP',
        validators=[MinValueValidator(0), MaxValueValidator(1000000000000)],
    )

    investment_secured_so_far = models.BigIntegerField(
        blank=True,
        null=True,
        help_text='Investment secured so far amount in GBP',
        validators=[MinValueValidator(0), MaxValueValidator(1000000000000)],
    )

    gross_development_value = models.BigIntegerField(
        blank=True,
        null=True,
        help_text='GDV amount in GBP',
        validators=[MinValueValidator(0), MaxValueValidator(1000000000000)],
    )

    capital_expenditure = models.BigIntegerField(
        blank=True,
        null=True,
        help_text='CapEx amount in GBP',
        validators=[MinValueValidator(0), MaxValueValidator(1000000000000)],
    )

    lead_dit_contact = models.ForeignKey(
        'company.Advisor',
        blank=True,
        related_name='+',
        on_delete=models.SET_NULL,
        null=True,
    )

    dit_contacts = models.ManyToManyField(
        'company.Advisor',
        related_name='+',
        blank=True,
    )

    status_detail = models.ForeignKey(
        'uk_opportunity.LargeCapitalUKOpportunityStatusDetails',
        blank=True,
        null=True,
        related_name='+',
        on_delete=models.SET_NULL,
    )


class LargeCapitalUKOpportunityStatusDetails(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
    )

    status = models.ForeignKey(
        'uk_opportunity.LargeCapitalUKOpportunityStatus',
        related_name='+',
        on_delete=models.PROTECT,
    )

    opportunity = models.ForeignKey(
        'uk_opportunity.LargeCapitalUKOpportunity',
        related_name='status_details_log',
        on_delete=models.CASCADE,
    )

    dit_supported = models.BooleanField(null=True)

    funding_source = models.ForeignKey(
        'uk_opportunity.LargeCapitalUKOpportunityFundingSource',
        related_name='+',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    abandonment_reason = models.ForeignKey(
        'uk_opportunity.LargeCapitalUKOpportunityAbandonmentReason',
        related_name='+',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )


class LargeCapitalUKOpportunityStatus(BaseOrderedConstantModel):
    """Large capital UK opportunity status metadata."""


class LargeCapitalUKOpportunityFundingSource(BaseOrderedConstantModel):
    """Large capital UK opportunity funding source metadata."""


class LargeCapitalUKOpportunityAbandonmentReason(BaseOrderedConstantModel):
    """Large capital UK opportunity funding source metadata."""
