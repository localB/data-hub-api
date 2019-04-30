from uuid import UUID

import pytest

from datahub.company.test.factories import CompanyFactory, ContactFactory
from datahub.investment.uk_opportunity.serializers import LargeCapitalUKOpportunitySerializer
from datahub.investment.uk_opportunity.test.factories import (
    CompleteLargeCapitalUKOpportunityFactory,
)

pytestmark = pytest.mark.django_db


class TestLargeCapitalInvestorProfileSerializer:
    """Tests for LargeCapitalInvestorProfileSerializer."""

    @pytest.mark.parametrize(
        'field,empty_value,expected_value',
        (
            ('total_investment_sought', None, None),
            ('investment_secured_so_far', None, None),
            ('investment_types', [], []),
            ('estimated_return_rate', '', None),
            ('time_scales', '', None),

            ('opportunity_description', '', ''),
            ('uk_region_locations', [], []),
            ('promoters', [], []),
            ('lead_dit_contact', '', None),
            ('asset_classes_of_interest', [], []),
            ('gross_development_value', None, None),
            ('construction_risks', [], []),

            ('capital_expenditure', None, None),
            ('dit_contacts', [], []),
            ('promoters', [], []),
        ),
    )
    def test_validate_fields_allow_null(self, field, empty_value, expected_value):
        """Test validates fields allow null or empty values."""
        opportunity = CompleteLargeCapitalUKOpportunityFactory()
        serializer = LargeCapitalUKOpportunitySerializer(
            data={field: empty_value},
            instance=opportunity,
            partial=True,
        )
        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data[field] == expected_value

    def test_incomplete_detail_fields(self):
        serializer = LargeCapitalUKOpportunitySerializer(data={'opportunity_name': 'hello'})
        assert serializer.is_valid(), serializer.errors
        serializer.save()
        assert serializer.validated_data == {'opportunity_name': 'hello'}
        assert 'incomplete_details_fields' in serializer.data
        assert serializer.data['incomplete_details_fields'] == [
            'opportunity_description',
            'uk_region_locations',
            'required_checks_conducted',
            'lead_dit_contact',
            'asset_classes_of_interest',
            'construction_risks',
            'value',
        ]

    def test_promoters(self):
        company = CompanyFactory()
        contact = ContactFactory()

        serializer = LargeCapitalUKOpportunitySerializer(
            data={
                'opportunity_name': 'hello',
                'promoters': [
                    {
                        'company': {
                            'id': company.pk,
                        },
                        'key_client_contact': {
                            'id': contact.pk,
                        },
                    },
                ],
            },
        )
        assert serializer.is_valid(), serializer.errors
        instance = serializer.save()
        assert instance.promoters.count() == 1
        assert serializer.validated_data == {
            'opportunity_name': 'hello',
            'promoters': [
                {
                    'company': company,
                    'key_client_contact': contact,
                },
            ],
        }

    def test_status(self):
        serializer = LargeCapitalUKOpportunitySerializer(
            data={
                'opportunity_name': 'hello',
                'status_details': {
                    'status': {
                        'id': UUID('fa2d3c77-66db-42ed-98e4-af974fe83986'),
                    },
                },
            },
        )
        assert serializer.is_valid(), serializer.errors
        instance = serializer.save()
        assert serializer.validated_data == {
            'opportunity_name': 'hello',
            'status_details': {
                'status': instance.status_detail.status,
            },
        }
