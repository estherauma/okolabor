
from django.urls import path

from recruiting.views.web import (
    EmployerCreateView, EmployerDetailView,
    EmployerListView, OkoMessageCreateView, OkoMessageListView, 
    RecruiterTodoView, RoleDeductionsCreateView, RoleEmpLocationCreateView,
    RoleHoursCreateView, RoleHousingCreateView, RoleMealsCreateView,
    RoleQualificationsCreateView, RoleWagesCreateView, WorkRequestCreateView,
    WorkRequestDetailView, WorkRequestRoleCreateView, WorkRequestsListView,
    OkoMessageDetailsView,RecruiterListView,AddRecruiterToEmployerView,RemoveRecruiterFromEmployerView,AccessDeniedView,AssignRecruiterView,SendRecruiterEmailView,AcceptRecruiterView,RejectRecruiterView,RemoveWorkerFromAssignmentView,UpdateStatusView,ContactWorkRequestsView,AssignEmployerContactView
)
from recruiting.views.workers import (
     WorkerCreateView, WorkerDetailsView, WorkerListView,AssignWorkerView,GetWorkerDetailsView,GetRolesForWorkRequestView
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
    path('workers/get-roles-for-work-request/<str:work_request_id>/', 
         GetRolesForWorkRequestView.as_view(), 
         name='get_roles_for_work_request'),
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
    path('workers/',
         WorkerListView.as_view(),
         name='workers'),
    path('assign-worker/', AssignWorkerView.as_view(), name='assign_worker'),
    path('get-worker-details/', GetWorkerDetailsView.as_view(), name='get_worker_details'),
    path('workers/<str:pk>/',
         WorkerDetailsView.as_view(),
         name='worker_detail'),
    path('workers/<pk>/workexperience/create/',
         CreateWorkExperienceView.as_view(),
         name='worker_experience_create'),
    path('message-details/<str:id>/', OkoMessageDetailsView.as_view(),
         name='message-details'),
    path('work-experience/<pk>/details', WorkExperienceDetailsView.as_view(),
         name='work_experience_details'),
    path("assign-recruiter/", AssignRecruiterView.as_view(), name="assign_recruiter"),
    path("send-recruiter-email/", SendRecruiterEmailView.as_view(), name="send_recruiter_email"),
    path("accept-recruiter/<str:employer_id>/<str:recruiter_id>/", AcceptRecruiterView.as_view(), name="accept_recruiter"),
    path("reject-recruiter/<str:employer_id>/<str:recruiter_id>/", RejectRecruiterView.as_view(), name="reject_recruiter"),

    path('recruiters/', RecruiterListView.as_view(), name='recruiter_list'),
    path('recruiters/add/<str:employer_id>/<str:recruiter_id>/', AddRecruiterToEmployerView.as_view(), name='add_recruiter_to_employer'),
    path('recruiters/remove/<str:employer_id>/<str:recruiter_id>/', RemoveRecruiterFromEmployerView.as_view(), name='remove_recruiter_from_employer'),
    path('access-denied/', AccessDeniedView.as_view(), name='access_denied'),

    path('remove-worker/<str:worker_id>/', RemoveWorkerFromAssignmentView.as_view(), name='remove_worker'),
    path('update-status/', UpdateStatusView.as_view(), name='update_status'),
    path('contacts/<str:contact_id>/work-requests/', ContactWorkRequestsView.as_view(), name='contact_work_requests'),
    path('assign-contact/', AssignEmployerContactView.as_view(), name='assign_employer_contact'),
]
