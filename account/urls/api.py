from django.urls import path
from account.views.api import RegisterView

app_name = 'account'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='api-register')
]
