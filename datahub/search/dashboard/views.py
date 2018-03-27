from oauth2_provider.contrib.rest_framework.permissions import IsAuthenticatedOrTokenHasScope
from rest_framework.response import Response
from rest_framework.views import APIView

from datahub.oauth.scopes import Scope
from datahub.search.contact.apps import ContactSearchApp
from datahub.search.elasticsearch import get_search_by_entity_query, limit_search_query
from datahub.search.interaction.apps import InteractionSearchApp
from datahub.search.permissions import has_permissions_for_app
from .serializers import HomepageSerializer


class IntelligentHomepageView(APIView):
    """Return the data for the intelligent homepage."""

    permission_classes = (IsAuthenticatedOrTokenHasScope,)

    required_scopes = (Scope.internal_front_end,)
    http_method_names = ['get']

    def get(self, request, format=None):
        """Implement GET method."""
        serializer = HomepageSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        limit = serializer.validated_data['limit']

        interactions = _get_objects(request, limit, InteractionSearchApp, 'dit_adviser.id')
        contacts = _get_objects(request, limit, ContactSearchApp, 'created_by.id')

        response = {
            'interactions': interactions,
            'contacts': contacts,
        }

        return Response(data=response)


def _get_objects(request, limit, search_app, adviser_field):
    if not has_permissions_for_app(request, search_app):
        return []

    query = get_search_by_entity_query(
        term='',
        entity=search_app.es_model,
        filter_data={
            adviser_field: request.user.id,
            'created_on_exists': True,
        },
        field_order='created_on:desc',
    )
    results = limit_search_query(
        query,
        offset=0,
        limit=limit,
    ).execute()

    return [result.to_dict() for result in results.hits]
