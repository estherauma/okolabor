from django.urls import path
from account.views.web import UpdatePasswordView, UserAccountView, UserActivitLogView, UserListView,AccountNotificationsView,WorkerModalCreateView,RecruiterAdminModalCreateView
from account.views.web import edit_user_view,edit_worker

urlpatterns = [
    path('', UserAccountView.as_view(), name='recruiter_account'),
    path('users/manage', UserListView.as_view(), name='manage_users'),
    path('activity-log', UserActivitLogView.as_view(), name='activity_log'),
    path('update-password/', UpdatePasswordView.as_view(), name='update_password'),
    path('notifications',AccountNotificationsView.as_view(),name='notifications'),
    path('edit-user/<str:curp>/', edit_user_view, name='edit_user'),
    path('edit-worker/<str:curp>/', edit_worker, name='edit_worker'),
    path('workers/modal-create/', WorkerModalCreateView.as_view(), name='worker_modal_create'),
    path('recruiter-admin/modal-create/', RecruiterAdminModalCreateView.as_view(), name='recruiter_admin_modal_create'),

]
