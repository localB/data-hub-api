"""Investment project models."""

import uuid

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from datahub.core.constants import InvestmentProjectPhase
from datahub.core.models import ArchivableModel, BaseModel
from datahub.investment.validate import (
    get_incomplete_reqs_fields, get_incomplete_team_fields,
    get_incomplete_value_fields
)

MAX_LENGTH = settings.CHAR_FIELD_MAX_LENGTH


class IProjectAbstract(models.Model):
    """The core part of an investment project."""

    class Meta:  # noqa: D101
        abstract = True

    name = models.CharField(max_length=MAX_LENGTH)
    description = models.TextField()
    nda_signed = models.BooleanField()
    estimated_land_date = models.DateField()
    investment_type = models.ForeignKey(
        'metadata.InvestmentType', on_delete=models.PROTECT,
        related_name='investment_projects'
    )

    cdms_project_code = models.CharField(max_length=MAX_LENGTH, blank=True,
                                         null=True)
    project_shareable = models.NullBooleanField()
    not_shareable_reason = models.TextField(blank=True, null=True)
    actual_land_date = models.DateField(blank=True, null=True)

    approved_commitment_to_invest = models.NullBooleanField()
    approved_fdi = models.NullBooleanField()
    approved_good_value = models.NullBooleanField()
    approved_high_value = models.NullBooleanField()
    approved_landed = models.NullBooleanField()
    approved_non_fdi = models.NullBooleanField()

    phase = models.ForeignKey(
        'metadata.InvestmentProjectPhase', on_delete=models.PROTECT,
        related_name='investment_projects',
        default=InvestmentProjectPhase.prospect.value.id
    )
    investor_company = models.ForeignKey(
        'company.Company', related_name='investor_investment_projects',
        null=True, blank=True, on_delete=models.CASCADE
    )
    intermediate_company = models.ForeignKey(
        'company.Company', related_name='intermediate_investment_projects',
        null=True, blank=True, on_delete=models.SET_NULL
    )
    client_contacts = models.ManyToManyField(
        'company.Contact', related_name='investment_projects', blank=True
    )
    client_relationship_manager = models.ForeignKey(
        'company.Advisor', related_name='investment_projects', null=True,
        blank=True, on_delete=models.SET_NULL
    )
    referral_source_adviser = models.ForeignKey(
        'company.Advisor', related_name='referred_investment_projects',
        null=True, blank=True, on_delete=models.SET_NULL
    )
    referral_source_activity = models.ForeignKey(
        'metadata.ReferralSourceActivity', related_name='investment_projects',
        null=True, blank=True, on_delete=models.SET_NULL
    )
    referral_source_activity_website = models.ForeignKey(
        'metadata.ReferralSourceWebsite', related_name='investment_projects',
        null=True, blank=True, on_delete=models.SET_NULL
    )
    referral_source_activity_marketing = models.ForeignKey(
        'metadata.ReferralSourceMarketing', related_name='investment_projects',
        null=True, blank=True, on_delete=models.SET_NULL
    )
    referral_source_activity_event = models.CharField(
        max_length=MAX_LENGTH, null=True, blank=True
    )
    fdi_type = models.ForeignKey(
        'metadata.FDIType', related_name='investment_projects', null=True,
        blank=True, on_delete=models.SET_NULL
    )
    non_fdi_type = models.ForeignKey(
        'metadata.NonFDIType', related_name='investment_projects', null=True,
        blank=True, on_delete=models.SET_NULL
    )
    sector = models.ForeignKey(
        'metadata.Sector', related_name='+', null=True, blank=True,
        on_delete=models.SET_NULL
    )
    business_activities = models.ManyToManyField(
        'metadata.InvestmentBusinessActivity',
        related_name='+',
        blank=True
    )

    @property
    def project_code(self):
        """A user-friendly project code.

        If a CDMS project code is held, that is returned. Otherwise a Data
        Hub project code beginning with DHP- is returned.
        """
        if self.cdms_project_code:
            return self.cdms_project_code
        project_num = self.investmentprojectcode.id
        return f'DHP-{project_num:08d}'


class IProjectValueAbstract(models.Model):
    """The value part of an investment project."""

    class Meta:  # noqa: D101
        abstract = True

    client_cannot_provide_total_investment = models.NullBooleanField()
    total_investment = models.DecimalField(null=True, max_digits=19,
                                           decimal_places=0, blank=True)
    client_cannot_provide_foreign_investment = models.NullBooleanField()
    foreign_equity_investment = models.DecimalField(
        null=True, max_digits=19, decimal_places=0, blank=True
    )
    government_assistance = models.NullBooleanField()
    number_new_jobs = models.IntegerField(null=True, blank=True)
    average_salary = models.ForeignKey(
        'metadata.SalaryRange', related_name='+', null=True, blank=True,
        on_delete=models.SET_NULL
    )
    number_safeguarded_jobs = models.IntegerField(null=True, blank=True)
    r_and_d_budget = models.NullBooleanField()
    non_fdi_r_and_d_budget = models.NullBooleanField()
    new_tech_to_uk = models.NullBooleanField()
    export_revenue = models.NullBooleanField()

    @property
    def value_complete(self):
        """Whether the value section is complete."""
        return not get_incomplete_value_fields(instance=self)


class IProjectRequirementsAbstract(models.Model):
    """The requirements part of an investment project."""

    class Meta:  # noqa: D101
        abstract = True

    client_requirements = models.TextField(blank=True, null=True)
    site_decided = models.NullBooleanField()
    address_line_1 = models.CharField(blank=True, null=True,
                                      max_length=MAX_LENGTH)
    address_line_2 = models.CharField(blank=True, null=True,
                                      max_length=MAX_LENGTH)
    address_line_3 = models.CharField(blank=True, null=True,
                                      max_length=MAX_LENGTH)
    address_line_postcode = models.CharField(blank=True, null=True,
                                             max_length=MAX_LENGTH)
    client_considering_other_countries = models.NullBooleanField()

    uk_company = models.ForeignKey(
        'company.Company', related_name='investee_projects',
        null=True, blank=True, on_delete=models.SET_NULL
    )
    competitor_countries = models.ManyToManyField('metadata.Country',
                                                  related_name='+', blank=True)
    uk_region_locations = models.ManyToManyField('metadata.UKRegion',
                                                 related_name='+', blank=True)
    strategic_drivers = models.ManyToManyField(
        'metadata.InvestmentStrategicDriver',
        related_name='investment_projects', blank=True
    )

    @property
    def requirements_complete(self):
        """Whether the requirements section is complete."""
        return not get_incomplete_reqs_fields(instance=self)


class IProjectTeamAbstract(models.Model):
    """The team part of an investment project."""

    class Meta:  # noqa: D101
        abstract = True

    project_manager = models.ForeignKey(
        'company.Advisor', null=True, related_name='+', blank=True,
        on_delete=models.SET_NULL
    )
    project_assurance_adviser = models.ForeignKey(
        'company.Advisor', null=True, related_name='+', blank=True,
        on_delete=models.SET_NULL
    )

    @property
    def project_manager_team(self):
        """The DIT team associated with the project manager."""
        if self.project_manager:
            return self.project_manager.dit_team
        return None

    @property
    def project_assurance_team(self):
        """The DIT team associated with the project assurance adviser."""
        if self.project_assurance_adviser:
            return self.project_assurance_adviser.dit_team
        return None

    @property
    def team_complete(self):
        """Whether the team section is complete."""
        return not get_incomplete_team_fields(instance=self)


class InvestmentProject(ArchivableModel, IProjectAbstract,
                        IProjectValueAbstract, IProjectRequirementsAbstract,
                        IProjectTeamAbstract, BaseModel):
    """An investment project."""

    id = models.UUIDField(primary_key=True, db_index=True, default=uuid.uuid4)

    def __str__(self):
        """Human-readable name for admin section etc."""
        company_name = self.investor_company or 'No company'
        return f'{company_name} – {self.name}'


class InvestmentProjectCode(models.Model):
    """An investment project number used for project codes.

    These are generated for new projects (but not for projects migrated
    from CDMS).

    This is required because Django does not allow AutoFields that are not
    primary keys, and we use UUIDs for primary keys. This model has a
    standard auto-incrementing integer (serial) as a primary key.
    """

    project = models.OneToOneField(InvestmentProject,
                                   on_delete=models.CASCADE)


@receiver(post_save, sender=InvestmentProject)
def project_post_save(sender, **kwargs):
    """Creates a project code for investment projects on creation.

    Projects with a CDMS project code do not get a new project code.
    """
    instance = kwargs['instance']
    created = kwargs['created']
    raw = kwargs['raw']
    if created and not raw and not instance.cdms_project_code:
        InvestmentProjectCode.objects.create(project=instance)
