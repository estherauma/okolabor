from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views import View
from django.views.generic import CreateView
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils.decorators import method_decorator
from django.contrib.auth.models import Group
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str

from account.models import User
from recruiting.utils import *
from recruiting.views.workers import WorkerDetailsView
from recruiting.forms import (
    EmployerForm,
    OkoMessageCreateForm,
    OkoMessageFilterForm,
    RoleDeductionForm,
    RoleEmploymentLocationForm,
    RoleHoursForm,
    RoleHousingInformationForm,
    RoleMealProvision,
    RoleQualificationForm,
    RoleWagesForm,
    TodoFilterForm,
    WorkRequestForm,
    WorkRequestRoleForm,
    WorkerAssignmentForm
)
from theme.forms import (
    FilterWorkExperienceForm,
    AdvancedFilterForm
)
from account.models import UserPreference
from recruiting.models import (
    Deduction,
    Employer,
    EmploymentLocation,
    Hours,
    HousingInformation,
    MealProvision,
    OkoMessage,
    Qualification,
    Role,
    Wages,
    WorkRequests,
    EmployerRecruiter,
    WorkAssignment,
)

class EmployerListView(View):
    def get(self, request):
        query = request.GET.get('query')
        employers_list = Employer.objects.all().prefetch_related('employerrecruiter_set')

        if query:
            employers_list = employers_list.filter(
                Q(name__icontains=query) |
                Q(email__icontains=query) |
                Q(address__icontains=query) |
                Q(country__icontains=query) |
                Q(phone__icontains=query)
            )

        paginator = Paginator(employers_list, 10)  # Show 10 employers per page
        page_number = request.GET.get('page')
        employers = paginator.get_page(page_number)

        recruiter_group = Group.objects.get(id=1)  # Adjust ID if necessary
        recruiters = recruiter_group.user_set.all()

        # Fetch recruiters assigned to employers
        employers_data = []
        for employer in employers:
            assigned_recruiters = EmployerRecruiter.objects.filter(employer=employer)
            recruiter_names = [rec.recruiter.get_full_name() for rec in assigned_recruiters]
            employer.recruiters = recruiter_names
            employers_data.append({
                'id': employer.id,
                'name': employer.name,
                'email': employer.email,
                'address': employer.address,
                'country': employer.country,
                'phone': employer.phone,
                'recruiters': recruiter_names  # List of recruiter names
            })

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'employers': employers_data,
                'has_more': employers.has_next()
            })
        context = {'employers': employers, 'query': query, 'recruiters': recruiters}
        return render(request, 'recruiting/employers/list.html', context)



class EmployerCreateView(CreateView):
    model = Employer
    form_class = EmployerForm
    template_name = 'recruiting/employers/create.html'

    def form_valid(self, form):
        messages.success(self.request, _('Employer created successfully'))
        return super(EmployerCreateView, self).form_valid(form)

    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{field}: {error}')
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse(
            'recruiting_web:employer_detail',
            kwargs={'pk': self.object.pk}
        )


class EmployerDetailView(View):
    def get(self, request, pk):
        employer = get_object_or_404(Employer, pk=pk)
        context = {'employer': employer}
        return render(request, 'recruiting/employers/detail.html', context)

# class WorkRequestsListView(View):
#     def get(self, request):
#         user = request.user  # Get logged-in recruiter

#         # Check if the user is part of the recruiter group
#         recruiter_group = Group.objects.get(id=1)  # Adjust ID if necessary
#         is_recruiter = recruiter_group.user_set.filter(id=user.id).exists()

#         # If user is not a recruiter, return an empty work request list
#         work_requests = WorkRequests.objects.none()
        
#         if is_recruiter:
#             # Get employers assigned to the recruiter
#             assigned_employers = EmployerRecruiter.objects.filter(recruiter=user).values_list("employer", flat=True)

#             # Fetch work requests linked to those employers
#             work_requests = WorkRequests.objects.filter(employer_id__in=assigned_employers)

#         context = {"work_requests": work_requests}
#         return render(request, "recruiting/work_requests/list.html", context)

class WorkRequestsListView(View):
    def get(self, request):
        work_requests = WorkRequests.objects.all()
        context = {'work_requests': work_requests}
        return render(request, 'recruiting/work_requests/list.html', context)

class WorkRequestCreateView(CreateView):
    model = WorkRequests
    form_class = WorkRequestForm
    template_name = 'recruiting/work_requests/create.html'

    def form_valid(self, form):
        messages.success(self.request, _('jobOrderCreatedSuccessfully'))
        return super(WorkRequestCreateView, self).form_valid(form)

    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{field}: {error}')
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse(
            'recruiting_web:workrequest_detail',
            kwargs={'pk': self.object.pk}
        )



class AddWorkersWorkRequests(View):
    def get(self, request, pk, role_id):
        work_assign_form = WorkerAssignmentForm()
        form = FilterWorkExperienceForm()
        filter_form = AdvancedFilterForm()
        search_query = request.GET.get('search', '')
        page_number = request.GET.get('page', 1)
        per_page = request.GET.get('per_page', 25)
        shortlisted_workers = get_shortlisted_workers()

        try:
            per_page = int(per_page)
        except ValueError:
            per_page = 4  # Fallback default

        # Retrieve the work request and role details using the provided IDs
        work_request = get_object_or_404(WorkRequests, pk=pk)
        role = get_object_or_404(Role, pk=role_id)

        work_requests = WorkRequests.objects.filter(status='Open').prefetch_related('roles')
        workers = User.objects.filter(groups__name='worker').order_by('-created_at')

        if search_query:
            workers = workers.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query)
            )

        paginator = Paginator(workers, per_page)
        page_obj = paginator.get_page(page_number)

        worker_data = []
        for worker in page_obj:
            profile_completion = calculate_profile_completion(worker)
            worker_details = get_worker_preferences(worker)

            worker.profile_completion_percentage = profile_completion
            latest_assignment = WorkAssignment.objects.filter(worker=worker).order_by('-assigned_date').first()
            worker.latest_status = latest_assignment.status if latest_assignment else "No Assignment"

            for key, value in worker_details.items():
                setattr(worker, key, value)

            worker_data.append({
                'id': worker.id,
                'firstname': worker.first_name,
                'lastname': worker.last_name,
                'email': worker.email,
                'profile_completion': profile_completion,
                **worker_details  # Merge worker details into response
            })

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'workers': worker_data, 'num_pages': paginator.num_pages})

        context = {
            'workers': page_obj,
            'work_requests': work_requests,
            'form': form,
            'work_assign_form': work_assign_form,
            'filter_form': filter_form,
            'search_query': search_query,
            'paginator': paginator,
            'per_page': per_page,
            'role': role,  # Pass the role details to the context
            'work_request': work_request,  # Pass the work request details to the context
            'shortlisted_workers': shortlisted_workers,
        }
        return render(request, 'recruiting/work_requests/create_addworker.html', context)

@method_decorator(csrf_exempt, name='dispatch')
class AddToShortlistView(View):

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        worker_ids = data.get('workerIds', [])

        if add_workers_to_shortlist(worker_ids):
            return JsonResponse({'success': True})

        return JsonResponse({'success': False})

class ShowWorkerDetails(View):
    def get(self, request, pk):
        view = WorkerDetailsView()
        return view.get(request, pk)


class WorkRequestDetailView(View):
    def get(self, request, pk):
        work_request = get_object_or_404(WorkRequests, pk=pk)
        
        # Filter WorkAssignments with 'Assigned' or 'Accepted' status
        active_workers = WorkAssignment.objects.filter(
            work_request=work_request, status__in=['Assigned', 'Accepted']
        ).select_related('worker')

        context = {
            'workrequest': work_request,
            'roles': work_request.roles.all(),
            'active_workers': active_workers,
        }
        return render(request, 'recruiting/work_requests/detail.html', context)


    

class WorkRequestRoleCreateView(CreateView):
    model = Role
    form_class = WorkRequestRoleForm
    template_name = 'recruiting/work_requests/create_role.html'

    def get_initial(self):
        initial = super().get_initial()
        initial['work_request'] = self.kwargs.get('pk')
        return initial

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        messages.success(self.request, _('addRoleRoleCreatedSuccessfully'))
        return super().form_valid(form)

    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{field}: {error}')
        return super().form_invalid(form)

    def get_success_url(self) -> str:
        return reverse(
            'recruiting_web:workrequest_detail',
            kwargs={'pk': self.object.work_request.pk}
        )


class RoleDataBaseView(CreateView):
    def get_initial(self):
        initial = super().get_initial()
        initial['role'] = self.kwargs.get('pk')
        return initial

    def get_success_url(self) -> str:
        return reverse(
            'recruiting_web:workrequest_detail',
            kwargs={'pk': self.object.role.work_request.pk}
        )

    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{field}: {error}')
        return super().form_invalid(form)

    def form_valid(self, form):
        form.instance.role_id = self.kwargs.get('pk')
        return super().form_valid(form)


class RoleHoursCreateView(RoleDataBaseView):
    model = Hours
    form_class = RoleHoursForm
    template_name = 'recruiting/work_requests/create_hours.html'

    def form_valid(self, form):
        messages.success(self.request, _('roleAddHoursRoleHoursSuccessfullyAdded'))
        return super().form_valid(form)


class RoleWagesCreateView(RoleDataBaseView):
    model = Wages
    form_class = RoleWagesForm
    template_name = 'recruiting/work_requests/create_wages.html'

    def form_valid(self, form):
        messages.success(self.request, _('roleWagesRolesWagesSuccessfullyAdded'))
        return super().form_valid(form)


class RoleDeductionsCreateView(RoleDataBaseView):
    model = Deduction
    form_class = RoleDeductionForm
    template_name = 'recruiting/work_requests/create_deductions.html'

    def form_valid(self, form):
        messages.success(self.request, _('roleDeductionsRolesDeductionsSuccessfullyAdded'))
        return super().form_valid(form)


class RoleQualificationsCreateView(RoleDataBaseView):
    model = Qualification
    form_class = RoleQualificationForm
    template_name = 'recruiting/work_requests/create_qualifications.html'


class RoleEmpLocationCreateView(RoleDataBaseView):
    model = EmploymentLocation
    form_class = RoleEmploymentLocationForm
    template_name = 'recruiting/work_requests/create_employment_location.html'

    def form_valid(self, form):
        messages.success(self.request, _('roleEmploymentLocationSuccessfullyAddedRoleLocation'))
        return super().form_valid(form)


class RoleHousingCreateView(RoleDataBaseView):
    model = HousingInformation
    form_class = RoleHousingInformationForm
    template_name = 'recruiting/work_requests/create_housing_info.html'

    def form_valid(self, form):
        messages.success(
            self.request,
            _('roleHousingInformationSuccessfullyAddedRoleHousingInformation')
        )
        return super().form_valid(form)


class RoleMealsCreateView(RoleDataBaseView):
    model = MealProvision
    form_class = RoleMealProvision
    template_name = 'recruiting/work_requests/create_meal_provision.html'

    def form_valid(self, form):
        messages.success(self.request,
                         _('roleMealProvisionSuccessfullyAddedRoleMealsInformation'))
        return super().form_valid(form)


class RecruiterTodoView(LoginRequiredMixin, View):
    def get(self, request):
        # initialize filter form
        form = TodoFilterForm()


        user = User.objects.get(pk=request.user.id)
        todos = WorkRequests.objects.exclude(
            status='completed'
        )
        context = {'todos': todos, 'user': user, 'form': form}
        return render(request, 'recruiting/todo.html', context)


class OkoMessageListView(View):
    def get(self, request):
        form = OkoMessageFilterForm()
        items = OkoMessage.objects.all()
        context = {'items': items, 'form': form }
        return render(request, 'recruiting/messages/list.html', context)


class OkoMessageCreateView(CreateView):
    model = OkoMessage
    form_class = OkoMessageCreateForm
    template_name = 'recruiting/messages/create.html'

    def form_valid(self, form):
        messages.success(self.request, _('messageCreatedSuccessfully'))
        return super(OkoMessageCreateView, self).form_valid(form)

    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{field}: {error}')
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse(
            'recruiting_web:recruiter_messages'
        )

class OkoMessageDetailsView(View):
    def get(self, request,id):
        print(request,id,"id")
        message = get_object_or_404(OkoMessage, pk=id)
        print(message,"message")
        context = {'message': message}
        return render(request, 'recruiting/messages/details.html',context)
    
@method_decorator(csrf_exempt, name='dispatch')
class AssignRecruiterView(View):
    def post(self, request):
        try:
            # Read and log the request body
            data = json.loads(request.body)
            employer_ids = data.get("employer_ids", [])
            recruiter_id = data.get("recruiter_id")
            
            if not employer_ids or not recruiter_id:
                return JsonResponse({"success": False, "error": "invalidData"}, status=400)

            # Check if recruiter exists
            try:
                recruiter_group = Group.objects.get(id=1)  # Adjust ID if necessary
                recruiters = recruiter_group.user_set.filter(id=recruiter_id)

                if not recruiters.exists():
                    return JsonResponse({"success": False, "error": "recruiterNotFoundInGroup"}, status=404)
                recruiter = recruiters.first()
            except User.DoesNotExist:
                return JsonResponse({"success": False, "error": "recruiterNotFoundInGroup"}, status=404)

            # Assign recruiter to employers
            employer_recruiter_objs = []
            for employer_id in employer_ids:
                try:
                    employer = Employer.objects.get(id=employer_id)
                    obj, created = EmployerRecruiter.objects.get_or_create(
                        employer=employer, recruiter=recruiter
                    )
                    employer_recruiter_objs.append(obj)
                except Employer.DoesNotExist:
                    print(f"Employer with ID {employer_id} not found")  # Debugging log


            return JsonResponse({"success": True, "assigned": len(employer_recruiter_objs)})

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "invalidJsonFormat"}, status=400)
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)
        
@method_decorator(csrf_exempt, name='dispatch')  # Disable CSRF for testing, remove this in production
class SendRecruiterEmailView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            employer_ids = data.get("employer_ids", [])
            recruiter_id = data.get("recruiter_id")

            if not employer_ids or not recruiter_id:
                return JsonResponse({"success": False, "error": "invalidJsonFormat"}, status=400)

            # Check if recruiter exists in the group
            try:
                recruiter_group = Group.objects.get(id=1)  # Adjust the group ID if necessary
                recruiters = recruiter_group.user_set.filter(id=recruiter_id)

                if not recruiters.exists():
                    return JsonResponse({"success": False, "error": "recruiterNotFoundInGroup"}, status=404)

                recruiter = recruiters.first()
                print(recruiter, "recruiter")

            except User.DoesNotExist:
                return JsonResponse({"success": False, "error": "recruiterNotFoundInGroup"}, status=404)

            # Send an email for each employer
            for employer_id in employer_ids:
                employer = get_object_or_404(Employer, id=employer_id)

                # Generate encoded links
                encoded_employer_id = urlsafe_base64_encode(force_bytes(employer.id))
                encoded_recruiter_id = urlsafe_base64_encode(force_bytes(recruiter.id))

                accept_url = request.build_absolute_uri(
                    reverse("recruiting_web:accept_recruiter", args=[encoded_employer_id, encoded_recruiter_id])
                )
                reject_url = request.build_absolute_uri(
                    reverse("recruiting_web:reject_recruiter", args=[encoded_employer_id, encoded_recruiter_id])
                )

                subject = "recruiterAssignmentRequest"
                message = f"""
                Hi {recruiter.first_name},

                You have been requested to be assigned as a recruiter for {employer.name}.

                Please choose an option:
                Accept: {accept_url}
                Reject: {reject_url}

                Regards,
                Team
                """

                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recruiter.email])

            return JsonResponse({"success": True, "message": "emailsSentSuccessfully!"})

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "invalidJsonFormat"}, status=400)
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)
        
class AcceptRecruiterView(View):
    def get(self, request, employer_id, recruiter_id, *args, **kwargs):
        try:
            # Decode the IDs
            employer_id = force_str(urlsafe_base64_decode(employer_id))
            recruiter_id = force_str(urlsafe_base64_decode(recruiter_id))
            employer = get_object_or_404(Employer, id=employer_id)
            recruiter = get_object_or_404(User, id=recruiter_id)
            # Assign recruiter to employer
            EmployerRecruiter.objects.get_or_create(employer=employer, recruiter=recruiter)
            # Send email to recruiter
            subject = "recruiterAssignmentAccepted"
            message = f"""
            Hi {recruiter.first_name},

            You have been assigned as a recruiter for {employer.name}.

            Regards,
            Team
            """

            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recruiter.email])
            
            return JsonResponse({"success": True, "message": "recruiterAssignmentAccepted"})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)
        
class RejectRecruiterView(View):
    def get(self, request, employer_id, recruiter_id, *args, **kwargs):
        try:
            # Decode the IDs
            employer_id = force_str(urlsafe_base64_decode(employer_id))
            recruiter_id = force_str(urlsafe_base64_decode(recruiter_id))

            employer = get_object_or_404(Employer, id=employer_id)
            recruiter = get_object_or_404(User, id=recruiter_id)
            return JsonResponse({"success": True, "message": "RecruiterAssignmentRejected!"})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)
