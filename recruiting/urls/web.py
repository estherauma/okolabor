from django.urls import path

from recruiting.views.web import (
    EmployerCreateView, EmployerDetailView,
    EmployerListView, WorkRequestCreateView,
    WorkRequestDetailView, WorkRequestRoleCreateView, WorkRequestsListView
)

app_name = 'recruiting_web'
urlpatterns = [
    path('employers/',
         EmployerListView.as_view(),
         name='employer_list'),
    path('employers/create/',
         EmployerCreateView.as_view(),
         name='employer_create'),
    path('employers/<pk>/',
         EmployerDetailView.as_view(),
         name='employer_detail'),
    path('work-requests/',
         WorkRequestsListView.as_view(),
         name='workrequest_list'),
    path('work-requests/create/',
         WorkRequestCreateView.as_view(),
         name='workrequest_create'),
    path('work-requests/<pk>/',
         WorkRequestDetailView.as_view(),
         name='workrequest_detail'),
    path('work-requests/<pk>/roles/create/',
         WorkRequestRoleCreateView.as_view(),
         name='workrequest_role_create'),
]
