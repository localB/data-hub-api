from django.utils.translation import gettext_lazy
from rest_framework import serializers

import datahub.metadata.models as meta_models
from datahub.core.serializers import NestedRelatedField
from datahub.core.validate_utils import is_not_blank
from datahub.core.validators import (
    AnyIsNotBlankRule,
    InRule,
    OperatorRule,
    RulesBasedValidator,
    ValidationRule,
)
from datahub.investment.investor_profile.constants import (
    REQUIRED_CHECKS_THAT_DO_NOT_NEED_ADDITIONAL_INFORMATION,
    REQUIRED_CHECKS_THAT_NEED_ADDITIONAL_INFORMATION,
)
from datahub.investment.investor_profile.models import (
    AssetClassInterest,
    ConstructionRisk,
    LargeCapitalInvestmentType,
    RequiredChecksConducted,
    ReturnRate,
    TimeHorizon,
)
from datahub.investment.investor_profile.validate import get_incomplete_fields
from datahub.investment.uk_opportunity.models import (
    LargeCapitalUKOpportunity,
    LargeCapitalUKOpportunityPromoter,
    LargeCapitalUKOpportunityStatusDetails,
)


BASE_FIELDS = [
    'id',
    'created_on',
    'modified_on',
    'status_detail',
]

INCOMPLETE_LIST_FIELDS = [
    'incomplete_details_fields',
    'incomplete_requirements_fields',
]

LARGE_CAPITAL_VALUE_DETAILS_FIELDS = [
    'capital_expenditure',
    'gross_development_value',
]

LARGE_CAPITAL_DETAILS_FIELDS = [
    'opportunity_name',
    'opportunity_description',
    'uk_region_locations',
    'required_checks_conducted',
    'lead_dit_contact',
    'promoters',
    'asset_classes_of_interest',
    'construction_risks',
]

LARGE_CAPITAL_ADDITIONAL_DETAILS_FIELDS = [
    'required_checks_conducted_on',
    'required_checks_conducted_by',
    'dit_contacts',
]


LARGE_CAPITAL_REQUIREMENTS_FIELDS = [
    'total_investment_sought',
    'investment_secured_so_far',
    'investment_types',
    'estimated_return_rate',
    'time_scales',
]


ALL_LARGE_CAPITAL_FIELDS = (
    BASE_FIELDS
    + INCOMPLETE_LIST_FIELDS
    + LARGE_CAPITAL_DETAILS_FIELDS
    + LARGE_CAPITAL_VALUE_DETAILS_FIELDS
    + LARGE_CAPITAL_ADDITIONAL_DETAILS_FIELDS
    + LARGE_CAPITAL_REQUIREMENTS_FIELDS
)


class LargeCapitalUKOpportunityPromoterSerializer(serializers.ModelSerializer):

    key_client_contact = NestedRelatedField(
        'company.Contact',
        required=False,
    )
    company = NestedRelatedField(
        'company.Company',
        allow_null=False,
    )

    class Meta:
        model = LargeCapitalUKOpportunityPromoter
        fields = ['key_client_contact', 'company']


class LargeCapitalUKOpportunityStatusDetailSerializer(serializers.ModelSerializer):
    status = NestedRelatedField(
        'uk_opportunity.LargeCapitalUKOpportunityStatus',
        required=True,
    )

    class Meta:
        model = LargeCapitalUKOpportunityStatusDetails
        fields = ['status']


class LargeCapitalUKOpportunitySerializer(serializers.ModelSerializer):
    """Large capital uk opportunity serializer."""

    default_error_messages = {
        'invalid_required_checks_conducted_on': gettext_lazy(
            'Enter the date of the most recent checks',
        ),
        'invalid_required_checks_conducted_by': gettext_lazy(
            'Enter the person responsible for the most recent checks',
        ),
        'required_checks_conducted_value': gettext_lazy(
            'Enter a value for required checks conducted',
        ),
    }

    opportunity_name = serializers.CharField(
        required=True,
    )

    opportunity_description = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
    )

    created_on = serializers.DateTimeField(
        read_only=True,
    )

    modified_on = serializers.DateTimeField(
        read_only=True,
    )

    required_checks_conducted = NestedRelatedField(
        RequiredChecksConducted,
        required=False,
    )

    required_checks_conducted_by = NestedRelatedField(
        'company.Advisor',
        required=False,
    )

    required_checks_conducted_on = serializers.DateField(
        required=False,
    )

    investment_types = NestedRelatedField(
        LargeCapitalInvestmentType,
        many=True,
        required=False,
    )

    estimated_return_rate = NestedRelatedField(
        ReturnRate,
        required=False,
        allow_null=True,
    )

    time_scales = NestedRelatedField(
        TimeHorizon,
        required=False,
        allow_null=True,
    )

    construction_risks = NestedRelatedField(
        ConstructionRisk,
        many=True,
        required=False,
    )

    uk_region_locations = NestedRelatedField(
        meta_models.UKRegion,
        many=True,
        required=False,
    )

    asset_classes_of_interest = NestedRelatedField(
        AssetClassInterest,
        many=True,
        required=False,
    )

    lead_dit_contact = NestedRelatedField(
        'company.Advisor',
        required=False,
        allow_null=True,
    )

    dit_contacts = NestedRelatedField(
        'company.Advisor',
        required=False,
        many=True,
    )
    promoters = LargeCapitalUKOpportunityPromoterSerializer(
        required=False,
        many=True,
    )
    status_detail = LargeCapitalUKOpportunityStatusDetailSerializer(
        required=False,
    )

    incomplete_details_fields = serializers.SerializerMethodField()

    incomplete_requirements_fields = serializers.SerializerMethodField()

    def create(self, validated_data):
        """
        Create an Large capital UK Opportunity.

        Overridden to handle updating of promoters.
        """
        return self._create_or_update(validated_data)

    def update(self, instance, validated_data):
        """
        Update a Large capital UK Opportunity.

        Overridden to handle updating of promoters.
        """
        return self._create_or_update(validated_data, instance=instance, is_update=True)

    def get_incomplete_details_fields(self, instance):
        """Returns a list of all the detail fields that are incomplete."""
        incomplete_details_fields = get_incomplete_fields(instance, LARGE_CAPITAL_DETAILS_FIELDS)

        incomplete_value_details_fields = get_incomplete_fields(
            instance, LARGE_CAPITAL_VALUE_DETAILS_FIELDS,
        )
        if set(incomplete_value_details_fields) == set(LARGE_CAPITAL_VALUE_DETAILS_FIELDS):
            incomplete_details_fields.append('value')
        return incomplete_details_fields

    def get_incomplete_requirements_fields(self, instance):
        """Returns a list of all the requirement fields that are incomplete."""
        return get_incomplete_fields(instance, LARGE_CAPITAL_REQUIREMENTS_FIELDS)

    def _create_or_update(self, validated_data, instance=None, is_update=False):
        """Overriding update to check required checks conducted data."""
        promoters = validated_data.pop('promoters', None)
        status_details = validated_data.pop('status_detail', None)

        if is_update:
            validated_data = self._update_required_checks_conducted(validated_data)
            uk_opportunity = super().update(instance, validated_data)
        else:
            uk_opportunity = super().create(validated_data)

        if promoters:
            uk_opportunity.promoters.all().delete()
            for promoter in promoters:
                LargeCapitalUKOpportunityPromoter.objects.get_or_create(
                    opportunity=uk_opportunity,
                    company=promoter['company'],
                    key_client_contact=promoter.get('key_client_contact'),
                )
        if status_details:

            details_obj, created = LargeCapitalUKOpportunityStatusDetails.objects.get_or_create(
                opportunity=uk_opportunity,
                status=status_details['status'],
            )
            if created:
                uk_opportunity.status_detail = details_obj
                uk_opportunity.save()

        return uk_opportunity

    def _update_required_checks_conducted(self, validated_data):
        """
        Checks if required checks conducted is being set to a setting that does not require
        the conditional data. If it is then the conditional fields are blanked.
        """
        if 'required_checks_conducted' in validated_data:
            if (
                    str(validated_data['required_checks_conducted'].id)
                    in REQUIRED_CHECKS_THAT_DO_NOT_NEED_ADDITIONAL_INFORMATION
            ):
                validated_data['required_checks_conducted_on'] = None
                validated_data['required_checks_conducted_by'] = None
        return validated_data

    class Meta:
        model = LargeCapitalUKOpportunity
        fields = ALL_LARGE_CAPITAL_FIELDS
        validators = [
            RulesBasedValidator(
                ValidationRule(
                    'invalid_required_checks_conducted_on',
                    OperatorRule('required_checks_conducted_on', bool),
                    when=InRule(
                        'required_checks_conducted',
                        REQUIRED_CHECKS_THAT_NEED_ADDITIONAL_INFORMATION,
                    ),
                ),
                ValidationRule(
                    'invalid_required_checks_conducted_by',
                    OperatorRule('required_checks_conducted_by', bool),
                    when=InRule(
                        'required_checks_conducted',
                        REQUIRED_CHECKS_THAT_NEED_ADDITIONAL_INFORMATION,
                    ),
                ),
                ValidationRule(
                    'required_checks_conducted_value',
                    OperatorRule('required_checks_conducted', is_not_blank),
                    when=AnyIsNotBlankRule(
                        'required_checks_conducted_by',
                        'required_checks_conducted_on',
                    ),
                ),
            ),
        ]
