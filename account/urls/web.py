from django.urls import path
from account.views.web import UpdatePasswordView, UserAccountView, UserActivitLogView, UserListView

urlpatterns = [
    path('', UserAccountView.as_view(), name='recruiter_account'),
    path('users/manage', UserListView.as_view(), name='manage_users'),
    path('activity-log', UserActivitLogView.as_view(), name='activity_log'),
    path('update-password/', UpdatePasswordView.as_view(), name='update_password'),
]
