from django.urls import path
from content.views import AggregatedContentView, ContentUpdateView, CompareContent

app_name = 'content'
urlpatterns = [
    path('aggregated/', AggregatedContentView.as_view(), name='aggregated'),
    path('compare/', CompareContent.as_view(), name='compare'),
    path('updated-webhook/', ContentUpdateView.as_view(), name='update'),
]
