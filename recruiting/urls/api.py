from django.urls import path

from recruiting.views.api import EmployerAPIListView


app_name = 'recruiting_api'

urlpatterns = [
    path('employers/', EmployerAPIListView.as_view(), name='employer_list'),
]
