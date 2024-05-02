from django.urls import path
from account.views.api import RegisterView, LoginView

app_name = 'account'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='api-register'),
    path('login', LoginView.as_view(), name='api-login')
]
