from django.urls import path

from datahub.investment.uk_opportunity.views import LargeCapitalUKOpportunityViewSet

GET_AND_POST_COLLECTION = {
    'get': 'list',
    'post': 'create',
}

GET_AND_PATCH_ITEM = {
    'get': 'retrieve',
    'patch': 'partial_update',
}

collection = LargeCapitalUKOpportunityViewSet.as_view(actions=GET_AND_POST_COLLECTION)

item = LargeCapitalUKOpportunityViewSet.as_view(actions=GET_AND_PATCH_ITEM)

urlpatterns = [
    path('large-capital/uk-opportunity', collection, name='collection'),
    path('large-capital/uk-opportunity/<uuid:pk>', item, name='item'),
]
