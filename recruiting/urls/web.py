from django.urls import path

from recruiting.views.web import EmployerCreateView, EmployerDetailView, EmployerListView


app_name = 'recruiting_web'
urlpatterns = [
    path('employers/', EmployerListView.as_view(), name='employer_list'),
    path('employers/create/', EmployerCreateView.as_view(), name='employer_create'),
    path('employers/<pk>/', EmployerDetailView.as_view(), name='employer_detail'),
]
