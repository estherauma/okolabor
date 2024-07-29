from django.urls import path

from recruiting.views.api import (
    EmployerAPIListView, WorkRequestRoleDetailView, WorkRequestsAPIListView
)


app_name = 'recruiting_api'

urlpatterns = [
    path('employers/', EmployerAPIListView.as_view(), name='employer_list'),
    path('work-requests/',
         WorkRequestsAPIListView.as_view(), name='work_requests_list'),
    path('role/<pk>/details/',
         WorkRequestRoleDetailView.as_view(), name='role_details'),
]
