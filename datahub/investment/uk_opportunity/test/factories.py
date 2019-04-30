import factory

from datahub.company.test.factories import AdviserFactory, CompanyFactory, ContactFactory
from datahub.core.constants import (
    UKRegion as UKRegionConstant,
)
from datahub.core.test.factories import to_many_field
from datahub.investment.investor_profile.test.constants import (
    AssetClassInterest as AssetClassInterestConstant,
    ConstructionRisk as ConstructionRiskConstant,
    LargeCapitalInvestmentTypes as InvestmentTypesConstant,
)


class LargeCapitalUKOpportunityFactory(factory.django.DjangoModelFactory):
    """Large Capital Investor profile factory."""

    opportunity_name = factory.Faker('name')

    @to_many_field
    def construction_risks(self):
        """Construction risks."""
        return []

    @to_many_field
    def asset_classes_of_interest(self):
        """Asset classes of interest."""
        return []

    @to_many_field
    def investment_types(self):
        """Investment types."""
        return []

    @to_many_field
    def uk_region_locations(self):
        """UK region locations."""
        return []

    @to_many_field
    def dit_contacts(self):
        """DIT Contacts."""
        return []

    @to_many_field
    def promoters(self):
        """Promoters."""
        return []

    class Meta:
        model = 'uk_opportunity.LargeCapitalUKOpportunity'


class CompleteLargeCapitalUKOpportunityFactory(LargeCapitalUKOpportunityFactory):
    """Complete Large Capital Investor profile factory."""

    opportunity_description = factory.Faker('text')
    total_investment_sought = 10000
    investment_secured_so_far = 20000

    @to_many_field
    def construction_risks(self):
        """Construction risks."""
        return [
            ConstructionRiskConstant.operational.value.id,
            ConstructionRiskConstant.greenfield.value.id,
        ]

    @to_many_field
    def asset_classes_of_interest(self):
        """Asset classes of interest."""
        return [
            AssetClassInterestConstant.biomass.value.id,
            AssetClassInterestConstant.biofuel.value.id,
        ]

    @to_many_field
    def investment_types(self):
        """Investment types."""
        return [
            InvestmentTypesConstant.direct_investment_in_project_equity.value.id,
        ]

    @to_many_field
    def uk_region_locations(self):
        """UK region locations."""
        return [
            UKRegionConstant.north_west.value.id,
            UKRegionConstant.north_east.value.id,
        ]

    @to_many_field
    def promoters(self):
        """Promoters."""
        return [
            LargeCapitalUKOpportunityPromoterFactory(opportunity=self),
        ]

    @to_many_field
    def dit_contacts(self):
        """DIT Contacts."""
        return [
            AdviserFactory(),
        ]


class LargeCapitalUKOpportunityPromoterFactory(factory.django.DjangoModelFactory):
    company = factory.SubFactory(CompanyFactory)
    key_client_contact = factory.SubFactory(ContactFactory)
    opportunity = factory.SubFactory(LargeCapitalUKOpportunityFactory)

    class Meta:
        model = 'uk_opportunity.LargeCapitalUKOpportunityPromoter'
