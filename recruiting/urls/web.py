from django.urls import path

from recruiting.views.web import (
    EmployerCreateView, EmployerDetailView,
    EmployerListView, OkoMessageCreateView, OkoMessageListView, 
    RecruiterTodoView, RoleDeductionsCreateView, RoleEmpLocationCreateView,
    RoleHoursCreateView, RoleHousingCreateView, RoleMealsCreateView,
    RoleQualificationsCreateView, RoleWagesCreateView, WorkRequestCreateView,
    WorkRequestDetailView, WorkRequestRoleCreateView, WorkRequestsListView,
    OkoMessageDetailsView
)
from recruiting.views.workers import (
     WorkerCreateView, WorkerDetailsView, WorkerListView
)

from recruiting.views.workers import (
     CreateWorkExperienceView, WorkExperienceDetailsView
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
    # Role relationships
    path('work-requests/role/<pk>/hours/create/',
         RoleHoursCreateView.as_view(),
         name='workrequest_hours_create'),
    path('work-requests/role/<pk>/wages/create/',
         RoleWagesCreateView.as_view(),
         name='workrequest_wages_create'),
    path('work-requests/role/<pk>/deductions/create/',
         RoleDeductionsCreateView.as_view(),
         name='workrequest_deductions_create'),
    path('work-requests/role/<pk>/qualifications/create/',
         RoleQualificationsCreateView.as_view(),
         name='workrequest_qualifications_create'),
    path('work-requests/role/<pk>/location/create/',
         RoleEmpLocationCreateView.as_view(),
         name='workrequest_role_create'),
    path('work-requests/role/<pk>/housing/create/',
         RoleHousingCreateView.as_view(),
         name='workrequest_role_create'),
    path('work-requests/role/<pk>/meals/create/',
         RoleMealsCreateView.as_view(),
         name='workrequest_role_create'),
    path('recruiter/todo/',
         RecruiterTodoView.as_view(),
         name='recruiter_todo'),
    path('recruiter/messages/',
         OkoMessageListView.as_view(),
         name='recruiter_messages'),
    path('recruiter/create-message/',
         OkoMessageCreateView.as_view(),
         name='recruiter_create_message'
         ),
    path('recruiter/create-worker',
         WorkerCreateView.as_view(),
         name='recruiter_create_worker'
         ),
    # Workers
    path('workers',
         WorkerListView.as_view(),
         name='workers'),
    path('workers/<pk>',
         WorkerDetailsView.as_view(),
         name='worker_detail'),
    path('workers/<pk>/workexperience/create/',
         CreateWorkExperienceView.as_view(),
         name='worker_experience_create'),
    path('message-details/<str:id>/', OkoMessageDetailsView.as_view(),
         name='message-details'),
    path('work-experience/<pk>/details', WorkExperienceDetailsView.as_view(),
         name='work_experience_details'),


]
