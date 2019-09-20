from django.db.models import F
from rest_framework import generics
from rest_framework import serializers
from rest_framework.views import APIView

from config.settings.types import HawkScope
from datahub.company.models.contact import Contact
from datahub.core.hawk_receiver import (
    HawkAuthentication,
    HawkResponseSigningMixin,
    HawkScopePermission,
)
from datahub.core.query_utils import (
    get_full_name_expression,
    get_string_agg_subquery,
)
from datahub.dataset.pagination import (
    ContactsDatasetViewCursorPagination,
    OMISDatasetViewCursorPagination,
)
from datahub.metadata.query_utils import get_sector_name_subquery
from datahub.omis.order.models import Order


class OMISDatasetView(HawkResponseSigningMixin, APIView):
    """
    An APIView that provides 'get' action which queries and returns desired fields for OMIS Dataset
    to be consumed by Data-flow periodically. Data-flow uses response result to insert data into
    Dataworkspace through its defined API endpoints. The goal is presenting various reports to the
    users out of flattened table and let analyst to work on denormalized table to get
    more meaningful insight.
    """

    authentication_classes = (HawkAuthentication, )
    permission_classes = (HawkScopePermission, )
    required_hawk_scope = HawkScope.data_flow_api
    pagination_class = OMISDatasetViewCursorPagination

    def get(self, request):
        """Endpoint which serves all records for OMIS Dataset"""
        dataset = self.get_dataset()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(dataset, request, view=self)
        return paginator.get_paginated_response(page)

    def get_dataset(self):
        """Returns list of OMIS Dataset records"""
        return Order.objects.annotate(
            sector_name=get_sector_name_subquery('sector'),
            services=get_string_agg_subquery(Order, 'service_types__name'),
        ).values(
            'cancellation_reason__name',
            'cancelled_on',
            'company__address_1',
            'company__address_2',
            'company__address_town',
            'company__address_county',
            'company__address_country__name',
            'company__address_postcode',
            'company__name',
            'company__registered_address_1',
            'company__registered_address_2',
            'company__registered_address_town',
            'company__registered_address_county',
            'company__registered_address_country__name',
            'company__registered_address_postcode',
            'completed_on',
            'contact__first_name',
            'contact__last_name',
            'contact__telephone_number',
            'contact__email',
            'created_by__dit_team__name',
            'created_on',
            'delivery_date',
            'invoice__subtotal_cost',
            'paid_on',
            'primary_market__name',
            'reference',
            'sector_name',
            'services',
            'status',
            'subtotal_cost',
            'uk_region__name',
        )


class ContactDatasetSerializer(serializers.ModelSerializer):
    
    company_sector = serializers.CharField()
    company_number = serializers.CharField()
    company_name = serializers.CharField()
    company_uk_region_name = serializers.CharField()

    class Meta:
        model = Contact
        fields = [
            'id',
            'accepts_dit_email_marketing',
            'address_postcode',
            'company_number',
            'company_name',
            'company_uk_region_name',
            'company_sector',
            'created_on',
            'email',
            'email_alternative',
            'job_title',
            'notes',
            'telephone_alternative',
            'telephone_number',
            'first_name',
            'last_name',
        ]


class ContactsDatasetView(generics.ListAPIView):
    """
    An APIView that provides 'get' action which queries and returns desired fields for
    Contacts Dataset to be consumed by Data-flow periodically. Data-flow uses response result
    to insert data into Dataworkspace through its defined API endpoints. The goal is presenting
    various reports to the users out of flattened table and let analyst to work on denormalized
    table to get more meaningful insight.
    """

    authentication_classes = (HawkAuthentication, )
    permission_classes = (HawkScopePermission, )
    required_hawk_scope = HawkScope.data_flow_api
    pagination_class = ContactsDatasetViewCursorPagination
    serializer_class = ContactDatasetSerializer

    def get_queryset(self):
        return Contact.objects.all().annotate(
            company_number=F('company__company_number'),
            company_name=F('company__name'),
            company_uk_region_name=F('company__uk_region__name'),
            company_sector=get_sector_name_subquery('company__sector'),
        ).select_related(
            'company',
            'company__uk_region',
            'company__sector',
        )
