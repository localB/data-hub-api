from django.db.models import Prefetch, Value, F, CharField

from datahub.activity_stream.omis.serializers import OMISOrderAddedSerializer
from datahub.activity_stream.pagination import ActivityCursorPagination
from datahub.activity_stream.views import ActivityViewSet
from datahub.omis.order.models import Order, OrderAssignee


class OMISOrderAddedPagination(ActivityCursorPagination):
    """
    OMIS Order added pagination for activity stream.
    """

    ordering = ('event_datetime', 'id')
    summary = 'OMIS Order Added Activity'


class OMISOrderAddedViewSet(ActivityViewSet):
    """
    OMIS Order added ViewSet for activity stream.
    """

    pagination_class = OMISOrderAddedPagination
    serializer_class = OMISOrderAddedSerializer

    def _get_base_queryset(self):
        queryset = Order.objects.select_related(
            'company',
            'contact',
            'created_by',
            'primary_market',
            'uk_region',
            'quote',
        ).prefetch_related(
            Prefetch('assignees', queryset=OrderAssignee.objects.order_by('pk')),
        )
        return queryset

    def get_queryset(self):
        created_orders = self._get_base_queryset().filter(created_on__isnull=False)\
            .annotate(event_status=Value("Add", output_field=CharField()))\
            .annotate(event_datetime=F('created_on'))
        quoted_orders = self._get_base_queryset().filter(quote__created_on__isnull=False)\
            .annotate(event_status=Value("Quoted", output_field=CharField()))\
            .annotate(event_datetime=F('quote__created_on'))
        accepted_orders = self._get_base_queryset().filter(quote__accepted_on__isnull=False)\
            .annotate(event_status=Value("Accepted", output_field=CharField()))\
            .annotate(event_datetime=F('quote__accepted_on'))
        paid_orders = self._get_base_queryset().filter(paid_on__isnull=False)\
            .annotate(event_status=Value("Paid", output_field=CharField()))\
            .annotate(event_datetime=F('paid_on'))
        completed_orders = self._get_base_queryset().filter(completed_on__isnull=False)\
            .annotate(event_status=Value("Completed", output_field=CharField()))\
            .annotate(event_datetime=F('completed_on'))
        cancelled_orders = self._get_base_queryset().filter(cancelled_on__isnull=False)\
            .annotate(event_status=Value("Cancelled", output_field=CharField()))\
            .annotate(event_datetime=F('cancelled_on'))

        all_order_statuses = created_orders\
            .union(quoted_orders)\
            .union(accepted_orders)\
            .union(paid_orders)\
            .union(completed_orders)\
            .union(cancelled_orders)
        return all_order_statuses
