from django.urls import path
from account.views.api import IndexView
app_name = 'account'

urlpatterns = [
    path('', IndexView.as_view(), name='api-home'),
]
