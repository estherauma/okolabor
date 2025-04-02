from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
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
)
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
        user = request.user
        query = request.GET.get('query')

        if user.groups.filter(name='admin').exists():
            employers_list = Employer.objects.all().prefetch_related('employerrecruiter_set')
        elif user.groups.filter(name='recruiter').exists():
            employers_list = Employer.objects.filter(employerrecruiter__recruiter=user).distinct()
        else:
            employers_list = Employer.objects.none()

        if query:
            employers_list = employers_list.filter(
                Q(name__icontains=query) |
                Q(email__icontains=query) |
                Q(address__icontains=query) |
                Q(country__icontains=query) |
                Q(phone__icontains=query)
            )

        paginator = Paginator(employers_list, 10)
        page_number = request.GET.get('page')
        employers = paginator.get_page(page_number)

        employers_data = []
        for employer in employers:
            assigned_recruiters = EmployerRecruiter.objects.filter(employer=employer)

            recruiter_names = list(set(rec.recruiter.get_full_name() for rec in assigned_recruiters if rec.recruiter == user))

            employers_data.append({
                'id': employer.id,
                'name': employer.name,
                'email': employer.email,
                'address': employer.address,
                'country': employer.country,
                'phone': employer.phone,
                'recruiters': recruiter_names
            })

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'employers': employers_data,
                'has_more': employers.has_next()
            })

        context = {'employers': employers_data, 'query': query}
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
        
        work_requests = WorkRequests.objects.filter(employer=employer)
        
        in_progress_work_requests = work_requests.filter(status__in=['Open', 'Requested'])
        closed_work_requests = work_requests.filter(status='Closed')
        draft_work_requests = work_requests.filter(status='Draft')

        recruiters = EmployerRecruiter.objects.filter(employer=employer).select_related('recruiter')
        context = {
            'employer': employer,
            'in_progress_work_requests': in_progress_work_requests,
            'closed_work_requests': closed_work_requests,
            'draft_work_requests': draft_work_requests,
            'recruiters': recruiters,
        }
        return render(request, 'recruiting/employers/detail.html', context)

class WorkRequestsListView(View):
    def get(self, request):
        user = request.user
        admin_group = Group.objects.get(name='admin')
        recruiter_group = Group.objects.get(name='recruiter')

        if admin_group in user.groups.all():
            work_requests = WorkRequests.objects.all()
        elif recruiter_group in user.groups.all():
            assigned_employers = EmployerRecruiter.objects.filter(recruiter=user).values_list("employer", flat=True)
            work_requests = WorkRequests.objects.filter(employer_id__in=assigned_employers)
        else:
            work_requests = WorkRequests.objects.none()

        context = {"work_requests": work_requests}
        return render(request, "recruiting/work_requests/list.html", context)


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


class WorkRequestDetailView(View):
    def get(self, request, pk):
        work_request = get_object_or_404(WorkRequests, pk=pk)
        active_workers = WorkAssignment.objects.filter(
            work_request=work_request, status__in=['Assigned', 'Accepted']
        ).select_related('worker')
        context = {
            'workrequest': work_request,
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

class RecruiterListView(LoginRequiredMixin, View):
    def get(self, request):
        if not request.user.groups.filter(name='recruiter_admin').exists():
            return redirect('recruiting_web:access_denied')

        recruiters = User.objects.filter(groups__name='recruiter').prefetch_related('employerrecruiter_set__employer')
        employers = Employer.objects.all()

        recruiter_data = []
        for recruiter in recruiters:
            assigned_employers = recruiter.employerrecruiter_set.all()
            employer_names = ", ".join([employer_recruiter.employer.name for employer_recruiter in assigned_employers])

            recruiter_data.append({
                "recruiter": recruiter,
                "employer_names": employer_names if employer_names else "Not Assigned any person"
            })
        return render(request, 'recruiting/recruiters/list.html', {'recruiters': recruiter_data, 'employers': employers})
    

class AddRecruiterToEmployerView(LoginRequiredMixin, View):
    def post(self, request, employer_id, recruiter_id):

        if not request.user.groups.filter(name='recruiter_admin').exists():
            return redirect('recruiting_web:access_denied')

        employer = get_object_or_404(Employer, id=employer_id)
        recruiter = get_object_or_404(User, id=recruiter_id)

        employer_recruiter, created = EmployerRecruiter.objects.get_or_create(employer=employer, recruiter=recruiter)

        if created:
            messages.success(request, _("Recruiter {email} assigned to {employer}.").format(email=recruiter.email, employer=employer.name))
        else:
            messages.info(request, _("Recruiter {email} is already assigned to {employer}.").format(email=recruiter.email, employer=employer.name))

        return redirect('recruiting_web:recruiter_list')


class RemoveRecruiterFromEmployerView(LoginRequiredMixin, View):
    def post(self, request, employer_id, recruiter_id):

        if not request.user.groups.filter(name='recruiter_admin').exists():
            return redirect('recruiting_web:access_denied')

        employer = get_object_or_404(Employer, id=employer_id)
        recruiter = get_object_or_404(User, id=recruiter_id)

        num_deleted, deleted_info = EmployerRecruiter.objects.filter(employer=employer, recruiter=recruiter).delete()

        if num_deleted > 0:
            messages.success(request, _("Recruiter {email} removed from {employer}.").format(email=recruiter.email, employer=employer.name))
        else:
            messages.info(request, _("Recruiter {email} was already removed from {employer}.").format(email=recruiter.email, employer=employer.name))

        return redirect('recruiting_web:recruiter_list')

            

class AccessDeniedView(View):
    def get(self, request):
        return render(request, 'recruiting/access_denied.html')



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
            try:
                recruiter_group = Group.objects.get(id=1)  # Adjust ID if necessary
                recruiters = recruiter_group.user_set.filter(id=recruiter_id)

                if not recruiters.exists():
                    return JsonResponse({"success": False, "error": "recruiterNotFoundInGroup"}, status=404)
                recruiter = recruiters.first()
            except User.DoesNotExist:
                return JsonResponse({"success": False, "error": "recruiterNotFoundInGroup"}, status=404)
            
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
            try:
                recruiter_group = Group.objects.get(id=1)  # Adjust the group ID if necessary
                recruiters = recruiter_group.user_set.filter(id=recruiter_id)

                if not recruiters.exists():
                    return JsonResponse({"success": False, "error": "recruiterNotFoundInGroup"}, status=404)

                recruiter = recruiters.first()
                print(recruiter, "recruiter")

            except User.DoesNotExist:
                return JsonResponse({"success": False, "error": "recruiterNotFoundInGroup"}, status=404)

            for employer_id in employer_ids:
                employer = get_object_or_404(Employer, id=employer_id)

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
            employer_id = force_str(urlsafe_base64_decode(employer_id))
            recruiter_id = force_str(urlsafe_base64_decode(recruiter_id))
            employer = get_object_or_404(Employer, id=employer_id)
            recruiter = get_object_or_404(User, id=recruiter_id)
            EmployerRecruiter.objects.get_or_create(employer=employer, recruiter=recruiter)
            
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
