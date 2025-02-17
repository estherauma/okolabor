from django.urls import path
from account.views.web import UpdatePasswordView, UserAccountView, UserActivitLogView, UserListView,AccountNotificationsView
from account.views.web import edit_user_view
urlpatterns = [
    path('', UserAccountView.as_view(), name='recruiter_account'),
    path('users/manage', UserListView.as_view(), name='manage_users'),
    path('activity-log', UserActivitLogView.as_view(), name='activity_log'),
    path('update-password/', UpdatePasswordView.as_view(), name='update_password'),
    path('notifications',AccountNotificationsView.as_view(),name='notifications'),
    path('edit-user/<str:curp>/', edit_user_view, name='edit_user'),

]
