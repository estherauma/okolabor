from django.urls import path

from recruiting.views.api import (
    EmployerAPIListView, RoleAPIListView, WorkRequestRoleDetailView, WorkRequestsAPIListView,AcceptRoleAPIView,RejectRoleAPIView
)


app_name = 'recruiting_api'

urlpatterns = [
    path('employers/', EmployerAPIListView.as_view(), name='employer_list'),
    path('work-requests/',
         WorkRequestsAPIListView.as_view(), name='work_requests_list'),
    path('roles/', RoleAPIListView.as_view(), name='role_list'),
    path('role/<pk>/details/',
         WorkRequestRoleDetailView.as_view(), name='role_details'),
    path('roles/<str:role_id>/accept', AcceptRoleAPIView.as_view(), name='role-accept'),
    path('roles/<str:role_id>/reject', RejectRoleAPIView.as_view(), name='role-reject'),
]
