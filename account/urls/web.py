from django.urls import path
from account.views.web import UserActivitLogView, UserListView

urlpatterns = [
    path('users/manage', UserListView.as_view(), name='manage_users'),
    path('activity-log', UserActivitLogView.as_view(), name='activity_log'),
]
