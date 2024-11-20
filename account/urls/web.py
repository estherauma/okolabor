from django.urls import path
from account.views.web import UserListView

urlpatterns = [
    path('users/manage', UserListView.as_view(), name='manage_users'),
]
