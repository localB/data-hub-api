from datahub.core.viewsets import CoreViewSet
from datahub.investment.uk_opportunity.models import LargeCapitalUKOpportunity
from datahub.investment.uk_opportunity.serializers import LargeCapitalUKOpportunitySerializer
from datahub.oauth.scopes import Scope


class LargeCapitalUKOpportunityViewSet(CoreViewSet):
    """Large capital uk opportunity view set."""

    required_scopes = (Scope.internal_front_end,)
    serializer_class = LargeCapitalUKOpportunitySerializer
    queryset = LargeCapitalUKOpportunity.objects.all()
