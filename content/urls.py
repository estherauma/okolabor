from django.urls import path
from content.views import (
    AggregatedContentView, ContentUpdateView, CompareContent,
    StartContentAggregation
)
app_name = 'content'

urlpatterns = [
    path('aggregated/', AggregatedContentView.as_view(), name='aggregated'),
    path('compare/', CompareContent.as_view(), name='compare'),
    path('start-aggregation/', StartContentAggregation.as_view(), name='start'),
    path('updated-webhook/', ContentUpdateView.as_view(), name='update'),
]
