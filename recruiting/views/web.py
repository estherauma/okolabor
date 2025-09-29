from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.urls import reverse,reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import CreateView,DeleteView,ListView
from django.views.decorators.csrf import csrf_exempt,csrf_protect
from django.views.decorators.http import require_POST
import json
from django.utils.translation import gettext as _
from dateutil.relativedelta import relativedelta
from django.utils.decorators import method_decorator
from django.contrib.auth.models import Group
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_decode
from django.utils import timezone,translation
from django.utils.encoding import force_str
from django.http import HttpResponseRedirect,HttpResponseForbidden
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from collections import defaultdict
from django.db.models import Count
from django.template.loader import render_to_string
import os
from common.firebase_utils import send_push_notification
from common.logger import AppLogger
from common.utils import StaticContent
from recruiting.utils import (
    get_worker_preferences, calculate_profile_completion,
    calculate_total_experience
)
from recruiting.models import Organization
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
    WorkerAssignmentForm,
    RoleEmploymentLocationForm,
    
)
from theme.forms import (
    FilterWorkExperienceForm,
    AdvancedFilterForm,
    DynamicWorkExperienceForm
)

from account.models import (
  UserPreference,
  UserWorkExperience,
  UserNotification
)
from recruiting.models import (
    Deduction,
    Organization,
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
    EmployerContact,
    EmployerRecruiterOrgLink,
)
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.forms.models import model_to_dict


class EmployerListView(View):
    def get(self, request):
        user = request.user
        query = request.GET.get('query')

        if user.groups.filter(name='admin').exists():
            employers_list = Organization.objects.filter(type='employer').order_by('name')

        elif user.groups.filter(name__in=['recruiter', 'recruiter_admin']).exists():
            
            recruiter_orgs = Organization.objects.filter(type='recruiter', recruiters=user).order_by('name')

            recruiter_links = EmployerRecruiterOrgLink.objects.filter(
                recruiter_org__in=recruiter_orgs,
                final_status='accepted'
            )
            employer_ids = recruiter_links.values_list('employer_org__id', flat=True)
            employers = Organization.objects.filter(id__in=employer_ids, type='employer').order_by('name')

            created_employers = Organization.objects.filter(type='employer', created_by=user).order_by('name')

            employers_list = (employers | created_employers).distinct()

        else:
            employers_list = Organization.objects.none()

        recruiter_organizations = Organization.objects.filter(type='recruiter').order_by('name')

        employers_data = []
        for employer in employers_list:
            links = EmployerRecruiterOrgLink.objects.filter(employer_org=employer, final_status='accepted').order_by('recruiter_org__name')
            recruiter_org_names = list(set(link.recruiter_org.name for link in links))

            employers_data.append({
                'id': employer.id,
                'name': employer.name,
                'email': employer.email,
                'address': employer.address,
                'country': employer.country,
                'phone': employer.phone,
                'website': employer.website,
                'city': employer.city,
                'state': employer.state,
                'zipcode': employer.zip_code,
                'description': employer.description,
                'recruiters': recruiter_org_names
            })
        employer_form = EmployerForm()

        context = {
            'employers': employers_data,
            'query': query,
            'recruiters': recruiter_organizations,
            'employer_form': employer_form,
            'breadcrumbs': [
                {'name': _('employersHome'), 'url': reverse_lazy('index')},
                {'name': _('employersEmployers'), 'url': None},
            ],
        }
        return render(request, 'recruiting/employers/list.html', context)

class EmployerDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        user = request.user
        employer = get_object_or_404(Organization, pk=pk, type='employer', deleted=False)
        
        if user.groups.filter(name='admin').exists():
            employer_name = employer.name
            employer.delete(user=user)
            
            messages.success(request, _('employersEmployer "%(employer_name)s" DeletedSuccessfully') % {'employer_name': employer_name})
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'})
            return redirect('recruiting_web:employer_list')

        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'forbidden'}, status=403)
            return HttpResponseForbidden(_("employersYouDoNotHavePermissionToDeleteThisEmployer"))

class EmployerEditView(LoginRequiredMixin, View):
    def post(self, request, pk):
        user = request.user
        employer = get_object_or_404(Organization, pk=pk, type='employer')

        if user.groups.filter(name='admin').exists():
            employer.name = request.POST.get('name')
            employer.email = request.POST.get('email')
            employer.phone = request.POST.get('phone')
            employer.website = request.POST.get('website')
            employer.address = request.POST.get('address')
            employer.city = request.POST.get('city')
            employer.state = request.POST.get('state')
            employer.country = request.POST.get('country')
            employer.zip_code = request.POST.get('zip_code')
            employer.description = request.POST.get('description')
            employer.save()

            messages.success(request, _('employersEmployer "%(employer_name)s" Edited Successfully.') % {'employer_name': employer.name})
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'})
            return redirect('recruiting_web:employer_list')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'forbidden'}, status=403)
            return HttpResponseForbidden(_("employersYouDoNotHavePermissionToEditThisEmployer"))

class RecruiterListViewInAdmin(View):
    def get(self, request):
        user = request.user
        query = request.GET.get('query')

        if user.groups.filter(name='admin').exists():
            recruiters_list = Organization.objects.filter(type='recruiter').order_by('name')
        else:
            recruiters_list = Organization.objects.none()

        # Apply search filter if present
        if query:
            recruiters_list = recruiters_list.filter(
                Q(name__icontains=query) |
                Q(email__icontains=query) |
                Q(address__icontains=query) |
                Q(city__icontains=query) |
                Q(country__icontains=query) |
                Q(phone__icontains=query)
            )

        recruiters = recruiters_list

        recruiters_data = []
        for recruiter in recruiters:
            assigned_links = EmployerRecruiterOrgLink.objects.filter(recruiter_org=recruiter).order_by('employer_org__name')
            assigned_employers = list(set(
                link.employer_org.name for link in assigned_links
            ))

            recruiters_data.append({
                'id': recruiter.id,
                'name': recruiter.name,
                'email': recruiter.email,
                'address': recruiter.address,
                'country': recruiter.country,
                'phone': recruiter.phone,
                'type': recruiter.type,
                'website': recruiter.website,
                'city': recruiter.city,
                'state': recruiter.state,
                'zip_code': recruiter.zip_code,
                'description': recruiter.description,
                'employers': assigned_employers
            })
        
        
        employer_form = EmployerForm()
        context = {'recruiters': recruiters_data, 
                   'query': query, 
                   'employer_form': employer_form,
                   'breadcrumbs': [
                            {'name': _('recruiterListHome'), 'url': reverse('index')},
                            {'name': _('recruiterListRecruiters'), 'url': None},
                        ],
                   }
        return render(request, 'recruiting/recruiters_list/list.html', context)


class RecruiterDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        user = request.user
        recruiter = get_object_or_404(Organization, pk=pk, type='recruiter',deleted=False)

        if user.groups.filter(name='admin').exists():
            recruiter_name = recruiter.name
            recruiter.delete(user=user)
            messages.success(request, _('recruiterAdminListRecruiter "%(recruiter_name)s" deletedSuccessfully.') % {'recruiter_name': recruiter_name})
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'})
            return redirect('recruiting_web:recruiter_admin_list')

        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'forbidden'}, status=403)
            return HttpResponseForbidden(_("recruiterAdminListYouDoNotHavePermissionToDeleteThisRecruiter"))

class RecruiterEditView(LoginRequiredMixin, View):
    def post(self, request, pk):
        user = request.user
        recruiter = get_object_or_404(Organization, pk=pk, type='recruiter')

        if user.groups.filter(name='admin').exists():
            recruiter_name = recruiter.name
            recruiter.name = request.POST.get('name')
            recruiter.email = request.POST.get('email')
            recruiter.phone = request.POST.get('phone')
            recruiter.website = request.POST.get('website')
            recruiter.address = request.POST.get('address')
            recruiter.city = request.POST.get('city')
            recruiter.state = request.POST.get('state')
            recruiter.country = request.POST.get('country')
            recruiter.zip_code = request.POST.get('zip_code')
            recruiter.description = request.POST.get('description')
            recruiter.save()

            messages.success(request, _('recruiterAdminListRecruiter "%(recruiter_name)s" editedSuccessfully.') % {'recruiter_name': recruiter.name})
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'})
            return redirect('recruiting_web:recruiter_admin_list')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'forbidden'}, status=403)
            return HttpResponseForbidden(_("recruiterAdminListYouDoNotHavePermissionToEditThisRecruiter"))

class EmployerCreateView(CreateView):
    model = Organization
    form_class = EmployerForm

    def get_initial(self):
        initial = super().get_initial()
        type_value = self.request.GET.get('type', 'recruiter')
        initial['type'] = type_value
        return initial

    def form_valid(self, form):
        org = form.save(commit=False)

        org_type = self.request.GET.get('type', 'recruiter')
        if org_type not in ['recruiter', 'employer']:
            org_type = 'recruiter'

        org.type = org_type
        org.created_by = self.request.user
        org.save()

        user = self.request.user

        if org_type == 'employer' and user.groups.filter(name__in=['recruiter', 'recruiter_admin']).exists():
            recruiter_orgs = Organization.objects.filter(type='recruiter', recruiters=user)

            for recruiter_org in recruiter_orgs:
                EmployerRecruiterOrgLink.objects.get_or_create(
                    employer_org=org,
                    recruiter_org=recruiter_org,
                    defaults={
                        'employer_status': 'accepted',
                        'recruiter_status': 'accepted',
                        'final_status': 'accepted'
                    }
                )
                EmployerRecruiterOrgLink.objects.get_or_create(
                    employer_org=org,
                    recruiter_org=recruiter_org,
                    defaults={
                        'employer_status': 'accepted',
                        'recruiter_status': 'accepted',
                        'final_status': 'accepted'
                    }
                )

        messages.success(self.request, _('employerAminListOrganizationCreatedSuccessfully'))
        self.object = org
        return redirect(self.get_success_url(org.pk))

    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{field}: {error}')
        return super().form_invalid(form)

    def get_success_url(self, pk):
        return reverse('recruiting_web:employer_detail', kwargs={'pk': pk})


class EmployerDetailView(View):
    def get(self, request, pk):
        user = request.user
        employer = get_object_or_404(Organization, pk=pk)

        work_requests = WorkRequests.objects.filter(employer=employer)
        in_progress_work_requests = work_requests.filter(status__in=['Open', 'Requested'])
        closed_work_requests = work_requests.filter(status='Closed')
        draft_work_requests = work_requests.filter(status='Draft')

        recruiters = EmployerRecruiter.objects.filter(employer=employer).select_related('recruiter')
        recruiter_names_direct = set(
            rec.recruiter.get_full_name()
            for rec in recruiters
            if user.groups.filter(name='admin').exists() or rec.recruiter == user
        )

        assigned_links = EmployerRecruiterOrgLink.objects.filter(employer_org=employer)
        recruiter_orgs = [link.recruiter_org for link in assigned_links]

        assigned_orgs_data = []
        recruiter_names_org = set()

        assigned_users = employer.recruiters.all()

        for org in recruiter_orgs:
            org_recruiters = org.recruiters.all()
            org_recruiter_names = [
                r.get_full_name()
                for r in org_recruiters
                if user.groups.filter(name='admin').exists() or r == user
            ]
            recruiter_names_org.update(org_recruiter_names)

            assigned_orgs_data.append({
                'id': org.id,
                'name': org.name,
                'email': org.email,
                'address': org.address,
                'country': org.country,
                'phone': org.phone,
                'recruiters': org_recruiter_names
            })

        all_recruiter_names = list(recruiter_names_direct.union(recruiter_names_org))
        users = User.objects.all()
        context = {
            'employer': employer,
            'users': users,
            'in_progress_work_requests': in_progress_work_requests,
            'closed_work_requests': closed_work_requests,
            'draft_work_requests': draft_work_requests,
            'recruiters': all_recruiter_names,
            'contacts': assigned_users,
            'work_requests': work_requests,
            'assigned_organizations': assigned_orgs_data,
            'breadcrumbs': [
                {'name': _('employerDetailsHome'), 'url': reverse_lazy('index')},
                {'name': _('employerDetailsEmployers'), 'url': reverse_lazy('recruiting_web:employer_list')},
                {'name': employer.name, 'url': None},
            ],
        }
        return render(request, 'recruiting/employers/detail.html', context)

class RecruiterDetailView(View):
    def get(self, request, pk):
        user = request.user
        recruiter_org = get_object_or_404(Organization, pk=pk, type='recruiter')

        org_link_employers = EmployerRecruiterOrgLink.objects.filter(recruiter_org=recruiter_org)
        org_employer_ids = org_link_employers.values_list('employer_org_id', flat=True)

        direct_employer_ids = EmployerRecruiter.objects.filter(
            recruiter__in=recruiter_org.recruiters.all()
        ).values_list('employer_id', flat=True)

        all_employer_ids = set(org_employer_ids) | set(direct_employer_ids)
        employer_orgs = Organization.objects.filter(id__in=all_employer_ids, type='employer').distinct()

        work_requests = WorkRequests.objects.filter(employer__in=employer_orgs)
        in_progress_work_requests = work_requests.filter(status__in=['Open', 'Requested'])
        closed_work_requests = work_requests.filter(status='Closed')
        draft_work_requests = work_requests.filter(status='Draft')

        employer_orgs_data = []
        for org in employer_orgs:
            employer_recruiters = EmployerRecruiter.objects.filter(employer=org)
            recruiter_names = list(set(
                rec.recruiter.get_full_name()
                for rec in employer_recruiters
                if user.groups.filter(name='admin').exists() or rec.recruiter == user
            ))
            employer_orgs_data.append({
                'id': org.id,
                'name': org.name,
                'email': org.email,
                'address': org.address,
                'country': org.country,
                'phone': org.phone,
                'recruiters': recruiter_names
            })
        assigned_users = recruiter_org.recruiters.all()
        # contacts = recruiter_org.contacts.all()
        users = User.objects.all()
        context = {
            'employer': recruiter_org,
            'users': users,
            'employer_organizations': employer_orgs_data,
            'in_progress_work_requests': in_progress_work_requests,
            'closed_work_requests': closed_work_requests,
            'draft_work_requests': draft_work_requests,
            'contacts': assigned_users,
            'work_requests': work_requests,
            'breadcrumbs': [
                            {'name': _('recruiterListHome'), 'url': reverse('index')},
                            {'name': _('recruiterListRecruiters'), 'url': reverse('recruiting_web:recruiter_admin_list')},
                            {'name': recruiter_org.name, 'url': None},
                        ],
        }
        return render(request, 'recruiting/recruiters_list/details.html', context)


class WorkRequestsListView(View):
    def get(self, request):
        user = request.user

        admin_group = Group.objects.get(name='admin')
        recruiter_group = Group.objects.get(name='recruiter')
        recruiter_admin_group = Group.objects.get(name='recruiter_admin')
        employer_group = Group.objects.get(name='employer')
        employer_admin_group = Group.objects.get(name='employer_admin')
        
       

        work_requests = WorkRequests.objects.none()

        if admin_group in user.groups.all():
            work_requests = WorkRequests.objects.all()

        elif recruiter_group in user.groups.all() or recruiter_admin_group in user.groups.all():
            user_orgs = user.organizations.all()
            if user_orgs.exists():
                assigned_employer_ids = EmployerRecruiterOrgLink.objects.filter(
                    recruiter_org__in=user_orgs
                ).values_list("employer_org_id", flat=True)
                work_requests = WorkRequests.objects.filter(employer_id__in=assigned_employer_ids)

        elif employer_group in user.groups.all() or employer_admin_group in user.groups.all():
            user_orgs = user.organizations.all()
            if user_orgs.exists():
                work_requests = WorkRequests.objects.filter(employer__in=user_orgs)

        for wr in work_requests:
            recruiter_link = EmployerRecruiterOrgLink.objects.filter(employer_org=wr.employer).first()
            wr.recruiter_org = recruiter_link.recruiter_org if recruiter_link else None
            
        form = WorkRequestForm()
        context = {
            "work_requests": work_requests,
            "employers": Organization.objects.filter(type='employer').order_by('name'),
            "recruiter": Organization.objects.filter(type='recruiter').order_by('name'),
            "form": form,
            "breadcrumbs": [
                        {'name': _('jobOrderListHome'), 'url': 'index'},
                        {'name': _('jobOrderListJobOrders'), 'url': None},
                    ],
        }
        return render(request, "recruiting/work_requests/list.html", context)


class DeleteAssignedOrganizationView(View):
    def post(self, request, employer_id, recruiter_org_id):
        employer = get_object_or_404(Organization, pk=employer_id)
        recruiter_org = get_object_or_404(Organization, pk=recruiter_org_id)

        EmployerRecruiterOrgLink.objects.filter(
            employer_org=employer,
            recruiter_org=recruiter_org
        ).delete()
        messages.success(self.request, _('employerAminListEmployerRecruiterDeletedSuccessfully'))
        return redirect('recruiting_web:employer_detail', pk=employer.id)


class DeleteEmployerOrganizationFromRecruiterView(View):
    def post(self, request, recruiter_org_id, employer_org_id):
        recruiter_org = get_object_or_404(Organization, pk=recruiter_org_id, type='recruiter')
        employer_org = get_object_or_404(Organization, pk=employer_org_id)

        EmployerRecruiterOrgLink.objects.filter(
            recruiter_org=recruiter_org,
            employer_org=employer_org
        ).delete()
        messages.success(self.request, _('employerAminListEmployerRecruiterDeletedSuccessfully'))

        return redirect('recruiting_web:recruiter_org_detail', pk=recruiter_org.id)


class WorkRequestCreateView(CreateView):
    model = WorkRequests
    form_class = WorkRequestForm

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, _('createJobOrderJobOrderCreatedSuccessfully'))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Form submission failed.')
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse('recruiting_web:workrequest_detail', kwargs={'pk': self.object.pk})

class WorkRequestEditView(LoginRequiredMixin, View):
    def post(self, request, pk):
        work_request = get_object_or_404(WorkRequests, pk=pk)
        form = WorkRequestForm(request.POST, instance=work_request)
        if form.is_valid():
            form.save()
            messages.success(request, _('jobOrderListWorkRequestEditedSuccessfully'))
            return redirect('recruiting_web:workrequest_detail', pk=work_request.pk)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
            return redirect('recruiting_web:workrequest_list')


class WorkRequestCopyView(LoginRequiredMixin, View):
    @staticmethod
    def copy_related_object(obj, model_class, new_role):
        if obj and getattr(obj, 'deleted_at', None) is None:
            data = model_to_dict(obj)
            data.pop('id', None)
            data['role'] = new_role
            model_class.objects.create(**data)

    def post(self, request, pk):
        work_request = get_object_or_404(WorkRequests, pk=pk)
        form = WorkRequestForm(request.POST)
        roles = work_request.roles.filter(
                deleted_at__isnull=True,
            )
     
        if form.is_valid():
            print(form.cleaned_data)
            new_work_request = form.save(commit=False)

            if work_request.name.strip().lower() == form.cleaned_data['name'].strip().lower():
                new_work_request.name = form.cleaned_data['name'] + " (Copy)"
            new_work_request.save()

            for role in roles:
                role_data = model_to_dict(role)
                role_data.pop('id', None)
                role_data['work_request'] = new_work_request
                new_role = Role.objects.create(**role_data)
                
                deductions = role.deductions.filter(deleted_at__isnull=True)
                for deduction in deductions:
                    data = model_to_dict(deduction)
                    data.pop('id', None)
                    data['role'] = new_role
                    Deduction.objects.create(**data)

                self.copy_related_object(getattr(role, 'hours', None), Hours, new_role)
                self.copy_related_object(getattr(role, 'employment_location', None), EmploymentLocation, new_role)
                self.copy_related_object(getattr(role, 'housing_information', None), HousingInformation, new_role)
                self.copy_related_object(getattr(role, 'wages', None), Wages, new_role)
                self.copy_related_object(getattr(role, 'meal_provision', None), MealProvision, new_role)
                self.copy_related_object(getattr(role, 'qualifications', None), Qualification, new_role)

            return redirect('recruiting_web:workrequest_detail', pk=new_work_request.pk)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
            return redirect('recruiting_web:workrequest_detail', pk=work_request.pk)
        
class WorkRequestDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        user = request.user
        work_request = get_object_or_404(WorkRequests, pk=pk)
        if user.groups.filter(name='admin').exists():
            work_request_name = work_request.name
            work_request.roles.all().delete()
            work_request.hard_delete()
            messages.success(
                request,
                _('jobOrderList "%(work_request_name)s" successfully deleted.') % {'work_request_name': work_request_name}
            )
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'})
            return redirect('recruiting_web:workrequest_list')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'forbidden'}, status=403)
            return HttpResponseForbidden(_("jobOrderListYouDoNotHavePermissionToDeleteThisJobOrder"))


@method_decorator(require_POST, name='dispatch')
class CopyWorkersView(View):
    def post(self, request):
        worker_ids = request.POST.getlist('worker_ids[]')
        work_request_id = request.POST.get('work_request')
        role_id = request.POST.get('role')
        status = request.POST.get('status', 'assigned')

        if not worker_ids or not work_request_id or not role_id:
            message = _('workersListInvalidRequestMissingData')
            messages.error(request, message)
            return JsonResponse({'success': False, 'response': message}, status=400)

        work_request = get_object_or_404(WorkRequests, id=work_request_id)
        role = get_object_or_404(Role, id=role_id)

        try:
            for worker_id in worker_ids:
                worker = get_object_or_404(User, id=worker_id)

                work_assignment, created = WorkAssignment.objects.get_or_create(
                    worker=worker,
                    role=role
                )
                work_assignment.work_request = work_request
                work_assignment.status = status
                work_assignment.save()

            success_message = _('workersListWorkersAssignedSuccessfully')
            messages.success(request, success_message)
            return JsonResponse({'success': True, 'response': success_message})

        except Exception as e:
            error_message = _('workersListAn Error Occurred: ') + str(e)
            messages.error(request, error_message)
            return JsonResponse({'success': False, 'response': error_message}, status=500)

class GetRolesView(View):
    def get(self, request, *args, **kwargs):
        work_request_id = request.GET.get('work_request_id')
        if not work_request_id:
            return JsonResponse({'error': 'Work request ID is required'}, status=400)

        try:
            work_request = WorkRequests.objects.filter(id=work_request_id).prefetch_related('roles').first()
            if not work_request:
                return JsonResponse({'error': 'Work request not found'}, status=404)

            roles_data = [{'id': role.id, 'title': role.title} for role in work_request.roles.all()]
            return JsonResponse({'roles': roles_data})
        except WorkRequests.DoesNotExist:
            return JsonResponse({'error': 'Work request not found'}, status=404)


@method_decorator(csrf_exempt, name='dispatch')
class UpdateWorkerStatusView(View):
    def post(self, request, *args, **kwargs):
        worker_ids = request.POST.getlist('worker_ids[]')
        work_request_id = request.POST.get('work_request')
        role_id = request.POST.get('role')

        if not work_request_id or not role_id:
            messages.error(request, 'Missing work request or role')
            return JsonResponse({'status': 'fail', 'message': 'Missing work request or role'}, status=400)

        work_request = get_object_or_404(WorkRequests, id=work_request_id)
        role = get_object_or_404(Role, id=role_id)

        user_push_tokens = []

        for worker_id in worker_ids:
            user = get_object_or_404(User, id=worker_id)

            assignments = WorkAssignment.objects.filter(
                worker=user,
                role=role,
                work_request=work_request
            )

            if assignments.exists():
                for assignment in assignments:
                    if assignment.status != 'offersent':
                        assignment.status = 'offersent'
                        assignment.save()
            else:
                WorkAssignment.objects.create(
                    worker=user,
                    role=role,
                    work_request=work_request,
                    status='offersent'
                )
                messages.success(request, f'Offer sent to {user.get_full_name()}')

            # Send notification
            if user.push_notification_token:
                user_push_tokens.append(user.push_notification_token)

            UserNotification.objects.create(
                user=user,
                title=_("workRequestAddNotificationTitle"),
                message=_("workRequestAddNotificationBody")
            )

        if user_push_tokens:
            send_push_notification(
                tokens=user_push_tokens,
                title=str(_("workRequestAddNotificationTitle")),
                body=str(_("workRequestAddNotificationBody")),
                data={'type': 'job_offer'}
            )

        messages.success(request, 'Offers sent successfully to selected workers.')

        return JsonResponse({
            'status': 'success',
            'success': 'True',
            'message': _('Offer sent successfully.')
        })
        
@method_decorator(csrf_exempt, name='dispatch')
class OfferSendWorkerView(View):
    def post(self, request, *args, **kwargs):
        worker_id = request.POST.get('worker_ids')
        work_request_id = request.POST.get('work_request')
        role_id = request.POST.get('role')
        status = request.POST.get('status', 'assigned')
        user = User.objects.get(id=worker_id)

        assignment = WorkAssignment.objects.filter(
            worker_id=worker_id,
            work_request_id=work_request_id,
            role_id=role_id,
            status='assigned'
        ).first()

        if assignment:
            assignment.status = 'offersent'
            assignment.save()
        else:
            WorkAssignment.objects.create(
                worker_id=worker_id,
                work_request_id=work_request_id,
                role_id=role_id,
                status='offersent'
            )
            
        current_lang = translation.get_language()
        try:
            translation.activate(user.language)
            UserNotification.objects.create(
                    user=user,
                    title=_("workRequestAddNotificationTitle"),
                    message= _("workRequestAddNotificationBody")
                )
        

            if user.push_notification_token:
                send_push_notification(
                    tokens=[user.push_notification_token],
                    title=str(_("workRequestAddNotificationTitle")),
                    body=str(_("workRequestAddNotificationBody")),
                    data={"type": "job_offer", "job_id": role_id},
            )
                
        finally:
            translation.activate(current_lang)
            
        messages.success(request, _("OfferSentSuccessfully."))

        return redirect('recruiting_web:worker_detail', pk=worker_id)


@method_decorator(csrf_exempt, name='dispatch')
class CancelOfferView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        worker_ids = data.get('worker_ids', [])
        WorkAssignment.objects.filter(
                worker_id__in=worker_ids,
                status__in=['offersent', 'assigned','confirmed']
            ).update(status='cancelled')
        messages.success(request, _("workRequestAddWorkerOfferCancelledSuccessfully"))
        return JsonResponse({'status': 'success', 'message': 'Offer cancelled successfully.'})

@method_decorator(csrf_exempt, name='dispatch')
class AddToShortlistView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        worker_ids = data.get('workerIds', [])
        work_request_id = data.get('workRequestId')
        role_id = data.get('roleId')

        work_request = get_object_or_404(WorkRequests, pk=work_request_id)
        role = get_object_or_404(Role, pk=role_id)

        added_any, already_assigned = add_workers_to_shortlist(worker_ids, work_request_id, role_id)

        if added_any:
            messages.success(request, "workRequestAddWorkerWorkersAddedToShortlistSuccessfully.")
            return JsonResponse({'success': True, 'message': _("workRequestAddWorkerWorkersAddedToShortlistSuccessfully")})
        else:
            messages.warning(request, "workRequestAddWorkerSomeWorkersAreAlreadyShortlisted.")
            return JsonResponse({'success': False, 'message': _("workRequestAddWorkerSomeWorkersAreAlreadyShortlisted")})


class ShowWorkerDetails(View):
    def get(self, request, pk):
        view = WorkerDetailsView()
        return view.get(request, pk)

class WorkRequestDetailView(View):
    def get(self, request, pk):
        work_request = get_object_or_404(WorkRequests, pk=pk)
        
        form_data  = RoleHoursForm
        grouped_counts = WorkAssignment.objects.filter(
            work_request=work_request,
            status__in=['assigned', 'offersent', 'confirmed']
        ).values('status', 'role__title').annotate(count=Count('id'))

        worker_summary = defaultdict(lambda: defaultdict(int))
        total_shortlist_count = 0
        total_offersent_count = 0
        total_confirmed_count = 0

        for item in grouped_counts:
            status = item['status']
            role = item['role__title']
            count = item['count']
            worker_summary[status][role] = count

            if status == 'assigned':
                total_shortlist_count += count
            elif status == 'offersent':
                total_offersent_count += count
            elif status == 'confirmed':
                total_confirmed_count += count

        roles_qs_raw = work_request.roles.filter(
                deleted_at__isnull=True,
            )
        roles_qs = [role for role in roles_qs_raw if hasattr(role, 'hours') and role.hours.deleted_at is None]
    
        role_forms = {
            role.id: WorkRequestRoleForm(instance=role)
            for 
            role in work_request.roles.all()
        }
        role_information_forms = {
            role.id: RoleEmploymentLocationForm(instance=role.employment_location)
            for role in work_request.roles.all() if hasattr(role, 'employment_location')
        }

        role_housing_information_forms = {
            role.id: RoleHousingInformationForm(instance=role.housing_information)
            for role in work_request.roles.all() if hasattr(role, 'housing_information')
        }

        role_meal_provision_forms = {
            role.id: RoleMealProvision(instance=role.meal_provision)
            for role in work_request.roles.all() if hasattr(role, 'meal_provision')
        }
        hours_form = {
            role.id: RoleHoursForm(instance=role.hours)
            for role in roles_qs if hasattr(role, 'hours')
            }
        wages_form = {
            role.id: RoleWagesForm(instance=role.wages)
            for role in roles_qs_raw if hasattr(role, 'wages') and role.wages and role.wages.deleted_at is None 
        }  
        qualification_forms = {
            role.id: RoleQualificationForm(instance=role.qualifications)
            for role in roles_qs_raw if hasattr(role, 'qualifications') and role.qualifications and role.qualifications.deleted_at is None
        }
        
        role_deductions = {
            role.id: role.deductions.filter()
            for role in roles_qs_raw
        }
        
        deduction_forms = {}
        for role in roles_qs_raw:
            deductions = role.deductions.filter()
            for deduction in deductions:
                deduction_forms[deduction.id] = RoleDeductionForm(instance=deduction)
        
        role_add_form = WorkRequestRoleForm(initial={'work_request': work_request})
        role_Hours_form = RoleHoursForm()
        role_Wages_form = RoleWagesForm()
        role_Deduction_form = RoleDeductionForm()
        role_Qualification_form = RoleQualificationForm()
        role_Employment_form = RoleEmploymentLocationForm()
        role_Housing_form = RoleHousingInformationForm()
        role_Meals_form = RoleMealProvision()
        
        # for item in roles_qs, find shortlist, offersent, confirmed and rejected count
        for item in roles_qs:
            item.shortlist_count = WorkAssignment.objects.filter(
                work_request=work_request,
                role=item,
                status='assigned'
            ).count()
            item.offersent_count = WorkAssignment.objects.filter(
                work_request=work_request,
                role=item,
                status='offersent'
            ).count()
            item.confirmed_count = WorkAssignment.objects.filter(
                work_request=work_request,
                role=item,
                status='confirmed'
            ).count()
            item.rejected_count = WorkAssignment.objects.filter(
                work_request=work_request,
                role=item,
                status='rejected'
            ).count()
        
        dynamic_fields = [
            'animal_types',
            'responsibilities_types',
            'crop_types',
            'crop_job_types',
            'mechanic_job_types',
            'supervision_jobs_types',
            'licensed_vehicle_operation_types',
        ]

        employers = Organization.objects.filter(type='employer')

        context = {
            'workrequest': work_request,
            'roles': roles_qs,
            'role_forms': role_forms,
            'worker_summary': worker_summary,
            'total_shortlist_count': total_shortlist_count,
            'total_offersent_count': total_offersent_count,
            'total_confirmed_count': total_confirmed_count,
            'role_information_forms': role_information_forms,
            'role_housing_information_forms': role_housing_information_forms,
            'role_meal_provision_forms': role_meal_provision_forms,
            'form': form_data,
            'hours_form': hours_form,
            'wages_form': wages_form,
            'qualification_form':qualification_forms,
            'role_deductions': role_deductions,
            'deduction_forms': deduction_forms,
            'role_Hours_form': role_Hours_form,
            'role_Wages_form': role_Wages_form,
            'role_Deduction_form': role_Deduction_form,
            'role_Qualification_form': role_Qualification_form,
            'role_Employment_form': role_Employment_form,
            'role_Housing_form': role_Housing_form,
            'role_Meals_form': role_Meals_form,
            'role_add_form': role_add_form,
            'dynamic_fields': dynamic_fields,
            'employers': employers,
            'breadcrumbs' :[
                        {'name': 'Home', 'url': reverse('index')},
                        {'name': 'Job Orders', 'url': reverse('recruiting_web:workrequest_list')},
                        {'name': work_request.name, 'url': None},
                    ],

        }
        return render(request, 'recruiting/work_requests/detail.html', context)
class WorkRequestRoleCreateView(CreateView):
    model = Role
    form_class = WorkRequestRoleForm

    def get_initial(self):
        initial = super().get_initial()
        initial['work_request'] = WorkRequests.objects.get(pk=self.kwargs['pk'])
        return initial

    def form_valid(self, form):
        messages.success(self.request, _('addRoleRoleCreatedSuccessfully'))
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{field}: {error}')
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse('recruiting_web:workrequest_detail', kwargs={'pk': self.object.work_request.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dynamic_fields'] = [
            'animal_types',
            'responsibilities_types',
            'crop_types',
            'crop_job_types',
            'mechanic_job_types',
            'supervision_jobs_types',
            'licensed_vehicle_operation_types',
        ]
        return context

class EditRoleView(View):
    def post(self, request, pk):
        role = get_object_or_404(Role, pk=pk)
        form = WorkRequestRoleForm(request.POST, instance=role)
        if form.is_valid():       
            form.save()
            messages.success(request, _('addRoleRoleUpdatedSuccessfully'))
            return redirect('recruiting_web:workrequest_detail', pk=role.work_request.pk)
        else:
            return redirect('recruiting_web:workrequest_detail', pk=role.work_request.pk)

class DeleteRoleView(View):
    def post(self, request, pk):
        role = get_object_or_404(Role, pk=pk)
        work_request_pk = role.work_request.pk 
        role.delete(user=request.user)
        messages.success(request, _('addRoleRoleDeletedSuccessfully'))
        return redirect('recruiting_web:workrequest_detail', pk=work_request_pk)

class RecruiterListView(LoginRequiredMixin, View):
    def get(self, request):
        if not request.user.groups.filter(name='recruiter_admin').exists():
            return redirect('recruiting_web:access_denied')

        recruiters = User.objects.filter(groups__name='recruiter').prefetch_related('employerrecruiter_set__employer').order_by('first_name')
        employers = Organization.objects.all()


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

        employer = get_object_or_404(Organization, id=employer_id)
        recruiter = get_object_or_404(User, id=recruiter_id)

        employer_recruiter, created = EmployerRecruiter.objects.get_or_create(employer=employer, recruiter=recruiter)

        if created:
            messages.success(request, _("recruiterAdminListRecruiter {email} assigned to {employer}.").format(email=recruiter.email, employer=employer.name))
        else:
            messages.info(request, _("Recruiter {email} is already assigned to {employer}.").format(email=recruiter.email, employer=employer.name))

        return redirect('recruiting_web:recruiter_list')


class RemoveRecruiterFromEmployerView(LoginRequiredMixin, View):
    def post(self, request, employer_id, recruiter_id):

        if not request.user.groups.filter(name='recruiter_admin').exists():
            return redirect('recruiting_web:access_denied')

        employer = get_object_or_404(Organization, id=employer_id)
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


class RoleHoursCreateView(CreateView):
    model = Hours
    form_class = RoleHoursForm

    def form_valid(self, form):
        role_id = self.kwargs['pk']
        role = get_object_or_404(Role.all_objects, pk=role_id)  # Use all_objects to bypass soft delete
        # If role has existing hours, hard delete them
        try:
            if role.hours and role.hours.deleted_at:
                role.hours.hard_delete()
        except ObjectDoesNotExist:
            pass

        # Prevent duplicates: check if Hours already exist for this role
        if Hours.objects.filter(role=role).exists():
            
            messages.warning(self.request, 'Hours already added for this role.')
            return redirect(reverse('recruiting_web:workrequest_detail', kwargs={
                'pk': role.work_request.pk
            }))

        form.instance.role = role
        self.object = form.save()
        messages.success(self.request, 'Hours successfully added.')
        return redirect(f'{reverse("recruiting_web:workrequest_detail", args=[role.work_request.pk])}?open_role={role.id}')

    def form_invalid(self, form):
        role_id = self.kwargs['pk']
        try:
            role = Role.all_objects.get(pk=role_id)
            work_request_pk = role.work_request.pk
        except Role.DoesNotExist:
            messages.error(self.request, 'Role not found.')
            return redirect('recruiting_web:workrequest_list')  # fallback view
        except Exception:
            messages.error(self.request, 'Something went wrong.')
            return redirect('recruiting_web:workrequest_list')

        messages.error(self.request, 'Failed to add hours. Please correct the errors.')
        return redirect(f'{reverse("recruiting_web:workrequest_detail", args=[work_request_pk])}?open_role={role.id}')
    

class RoleWagesCreateView(CreateView):
    model = Wages
    form_class = RoleWagesForm

    def form_valid(self, form):
        role_id = self.kwargs['pk']
        role = get_object_or_404(Role.all_objects, pk=role_id)
        # If role has existing wages, hard delete them
        try:
            if role.wages and role.wages.deleted_at:
                role.wages.hard_delete()
        except ObjectDoesNotExist:
            pass

        # Check for existing wages
        if Wages.objects.filter(role=role).exists():
            messages.warning(self.request, 'Wages already added for this role.')
            return redirect(reverse('recruiting_web:workrequest_detail', kwargs={
                'pk': role.work_request.pk
            }))

        form.instance.role = role  # assign manually
        self.object = form.save()
        messages.success(self.request, 'Wages successfully added.')
        return redirect(f'{reverse("recruiting_web:workrequest_detail", args=[role.work_request.pk])}?open_role={role.id}')


    def form_invalid(self, form):
        messages.error(self.request, 'Failed to add wages. Please correct the errors.')
        role_id = self.kwargs['pk']
        try:
            role = Role.all_objects.get(pk=role_id)
            work_request_pk = role.work_request.pk
        except Role.DoesNotExist:
            return redirect('recruiting_web:workrequest_list')

        return redirect(f'{reverse("recruiting_web:workrequest_detail", args=[work_request_pk])}?open_role={role.id}')


class RoleDeductionsCreateView(CreateView):
    model = Deduction
    form_class = RoleDeductionForm

    def form_valid(self, form):
        role_id = self.kwargs['pk']
        role = get_object_or_404(Role.all_objects, pk=role_id)

        form.instance.role = role
        self.object = form.save()
        messages.success(self.request, 'Deductions successfully added.')
        return redirect(f'{reverse("recruiting_web:workrequest_detail", args=[role.work_request.pk])}?open_role={role.id}')


    def form_invalid(self, form):
        messages.error(self.request, 'Failed to add deductions. Please correct the errors.')
        try:
            role = Role.all_objects.get(pk=self.kwargs['pk'])
            return redirect(f'{reverse("recruiting_web:workrequest_detail", args=[role.work_request.pk])}?open_role={role.id}')

        except Role.DoesNotExist:
            return redirect('recruiting_web:workrequest_list')

class RoleQualificationsCreateView(CreateView):
    model = Qualification
    form_class = RoleQualificationForm

    def form_valid(self, form):
        role_id = self.kwargs['pk']
        role = get_object_or_404(Role.all_objects, pk=role_id)
        # If role has existing qualifications, hard delete them
        try:
            if role.qualifications and role.qualifications.deleted_at:
                role.qualifications.hard_delete()
        except ObjectDoesNotExist:
            pass

        if Qualification.objects.filter(role=role).exists():
            messages.warning(self.request, 'Qualifications already added for this role.')
            return redirect(f'{reverse("recruiting_web:workrequest_detail", args=[role.work_request.pk])}?open_role={role.id}')

        form.instance.role = role
        self.object = form.save()
        messages.success(self.request, 'Qualifications successfully added.')
        return redirect(f'{reverse("recruiting_web:workrequest_detail", args=[role.work_request.pk])}?open_role={role.id}')

    def form_invalid(self, form):
        messages.error(self.request, 'Failed to add qualifications. Please correct the errors.')
        try:
            role = Role.all_objects.get(pk=self.kwargs['pk'])
            return redirect(f'{reverse("recruiting_web:workrequest_detail", args=[role.work_request.pk])}?open_role={role.id}')
        except Role.DoesNotExist:
            return redirect('recruiting_web:workrequest_list')


class RoleEmpLocationCreateView(CreateView):
    model = EmploymentLocation
    form_class = RoleEmploymentLocationForm

    def form_valid(self, form):
        role_id = self.kwargs['pk']
        role = get_object_or_404(Role.all_objects, pk=role_id)
        try:
            if role.employment_location and role.employment_location.deleted_at:
                role.employment_location.hard_delete()
        except ObjectDoesNotExist:
            pass

        if EmploymentLocation.objects.filter(role=role).exists():
            messages.warning(self.request, 'Employment location already added for this role.')
            return redirect(f'{reverse("recruiting_web:workrequest_detail", args=[role.work_request.pk])}?open_role={role.id}')

        form.instance.role = role
        self.object = form.save()
        messages.success(self.request, 'Employment location successfully added.')
        return redirect(f'{reverse("recruiting_web:workrequest_detail", args=[role.work_request.pk])}?open_role={role.id}')

    def form_invalid(self, form):
        role_id = self.kwargs['pk']
        try:
            role = Role.all_objects.get(pk=role_id)
            work_request_pk = role.work_request.pk
        except Role.DoesNotExist:
            return redirect('recruiting_web:workrequest_list')

        messages.error(self.request, 'Failed to add employment location. Please correct the errors.')
        return redirect(f'{reverse("recruiting_web:workrequest_detail", args=[work_request_pk])}?open_role={role.id}')

class RoleHousingCreateView(CreateView):
    model = HousingInformation
    form_class = RoleHousingInformationForm

    def form_valid(self, form):
        role_id = self.kwargs['pk']
        role = get_object_or_404(Role.all_objects, pk=role_id)
        # If role has existing housing information, hard delete it
        try:
            if role.housing_information and role.housing_information.deleted_at:
                role.housing_information.hard_delete()
        except ObjectDoesNotExist:
            pass

        # Prevent duplicate housing info
        if HousingInformation.objects.filter(role=role).exists():
            messages.warning(self.request, 'Housing information already added for this role.')
            return redirect(f'{reverse("recruiting_web:workrequest_detail", args=[role.work_request.pk])}?open_role={role.id}')

        form.instance.role = role
        self.object = form.save()
        messages.success(self.request, 'Housing information successfully added.')
        return redirect(f'{reverse("recruiting_web:workrequest_detail", args=[role.work_request.pk])}?open_role={role.id}')

    def form_invalid(self, form):
        role_id = self.kwargs['pk']
        try:
            role = Role.all_objects.get(pk=role_id)
            work_request_pk = role.work_request.pk
        except Role.DoesNotExist:
            return redirect('recruiting_web:workrequest_list')

        messages.error(self.request, 'Failed to add housing information. Please correct the errors.')
        return redirect(f'{reverse("recruiting_web:workrequest_detail", args=[work_request_pk])}?open_role={role.id}')


class RoleMealsCreateView(CreateView):
    model = MealProvision
    form_class = RoleMealProvision

    def form_valid(self, form):
        role_id = self.kwargs['pk']
        role = get_object_or_404(Role.all_objects, pk=role_id)
        # If role has existing meal provision, hard delete it
        try:
            if role.meal_provision and role.meal_provision.deleted_at:
                role.meal_provision.hard_delete()
        except ObjectDoesNotExist:
            pass

        # Check if MealProvision already exists for this role
        if MealProvision.objects.filter(role=role).exists():
            messages.warning(self.request, 'Meal Provision already added for this role.')
            return redirect(f'{reverse("recruiting_web:workrequest_detail", args=[role.work_request.pk])}?open_role={role.id}')

        form.instance.role = role
        self.object = form.save()
        messages.success(self.request, 'Meal Provision successfully added.')
        return redirect(f'{reverse("recruiting_web:workrequest_detail", args=[role.work_request.pk])}?open_role={role.id}')

    def form_invalid(self, form):
        messages.error(self.request, 'Failed to add Meal Provision. Please correct the errors.')
        try:
            role = Role.all_objects.get(pk=self.kwargs['pk'])
            work_request_pk = role.work_request.pk
        except Role.DoesNotExist:
            return redirect('recruiting_web:workrequest_list')

        return redirect(f'{reverse("recruiting_web:workrequest_detail", args=[work_request_pk])}?open_role={role.id}')


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
        context = {'items': items, 
                   'form': form ,
                    'breadcrumbs': [
                        {'name': _('messagesHome'), 'url': reverse_lazy('index')},
                        {'name': _('messagesMessages'), 'url': None},
                    ],
                   }
        return render(request, 'recruiting/messages/list.html', context)


class OkoMessageCreateView(CreateView):
    model = OkoMessage
    form_class = OkoMessageCreateForm
    template_name = 'recruiting/messages/create.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
            {'name': _('createMessageHome'), 'url': reverse_lazy('index')},
            {'name': _('createMessageMessages'), 'url': reverse_lazy('recruiting_web:recruiter_messages')},
            {'name': _('createMessageCreateMessage'), 'url': None},
        ]
        return context

    def form_valid(self, form):
        messages.success(self.request, _('createMessageMessageCreatedSuccessfully'))
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
        message = get_object_or_404(OkoMessage, pk=id)
        context = {'message': message,
                   'breadcrumbs': [
                            {'name': _('messageDetailsHome'), 'url': reverse('index')},
                            {'name': _('messageDetailsMessages'), 'url': reverse('recruiting_web:recruiter_messages')},
                            {'name': _('messageDetailsMessageDetails'), 'url': None},
                        ],
                   }
        return render(request, 'recruiting/messages/details.html',context)

class AssignRecruiterView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            employer_ids = data.get("employer_ids", [])
            recruiter_id = data.get("recruiter_id")

            if not employer_ids or not recruiter_id:
                return JsonResponse({"success": False, "error": "invalidDataProvidedMissingEmployerIdsOrRecruiterId."}, status=400)

            recruiter_group = Group.objects.filter(name="Recruiter").first()
            if not recruiter_group:
                return JsonResponse({"success": False, "error": "recruiterGroupNotFound."}, status=404)

            recruiter = recruiter_group.user_set.filter(id=recruiter_id).first()
            if not recruiter:
                return JsonResponse({"success": False, "error": "recruiterNotFoundInRecruiterGroup."}, status=404)

            assigned_employers = []
            not_found_employers = []

            for employer_id in employer_ids:
                try:
                    employer = Organization.objects.get(id=employer_id)
                    obj, created = EmployerRecruiter.objects.get_or_create(
                        employer=employer, recruiter=recruiter
                    )
                    assigned_employers.append(employer_id)
                except ObjectDoesNotExist:
                    not_found_employers.append(employer_id)

            response_data = {
                "success": True,
                "message": f"successfullyAssignedRecruiterTo{len(assigned_employers)}Employers.",
                "assignedEmployers": assigned_employers,
                "notFoundEmployers": not_found_employers,
            }

            if not_found_employers:
                response_data["warning"] = f"employersWithIds{not_found_employers}NotFound."

            return JsonResponse(response_data)

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "invalidJsonFormat."}, status=400)

        except Exception as e:
            return JsonResponse({"success": False, "error": f"anErrorOccurred{str(e)}"}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class SendRecruiterEmailView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            employer_ids = data.get("employer_ids", [])
            recruiter_id = data.get("recruiter_id")

            if not employer_ids or not recruiter_id:
                return JsonResponse({"success": False, "error": "invalidJsonFormatMissingEmployerIdsOrRecruiterId."}, status=400)

            recruiter_group = Group.objects.filter(id=1).first()
            if not recruiter_group:
                return JsonResponse({"success": False, "error": "recruiterGroupNotFound."}, status=404)

            recruiters = recruiter_group.user_set.filter(id=recruiter_id)
            if not recruiters.exists():
                return JsonResponse({"success": False, "error": "recruiterNotFoundInGroup."}, status=404)

            recruiter = recruiters.first()

            for employer_id in employer_ids:
                employer = get_object_or_404(Organization, id=employer_id)
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

            return JsonResponse({"success": True, "message": "emailsSentSuccessfully."})

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "invalidJsonFormat."}, status=400)
        
        except Exception as e:
            return JsonResponse({"success": False, "error": f"anErrorOccurred{str(e)}"}, status=500)

class AcceptRecruiterView(View):
    def get(self, request, employer_id, recruiter_id, *args, **kwargs):
        try:
            employer_id = force_str(urlsafe_base64_decode(employer_id))
            recruiter_id = force_str(urlsafe_base64_decode(recruiter_id))

            employer = get_object_or_404(Organization, id=employer_id)
            recruiter = get_object_or_404(User, id=recruiter_id)

            obj, created = EmployerRecruiter.objects.get_or_create(employer=employer, recruiter=recruiter)

            subject = "recruiterAssignmentAccepted"
            message = f"""
            Hi {recruiter.first_name},

            You have been assigned as a recruiter for {employer.name}.

            Regards,
            Team
            """
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recruiter.email])
            
            message = _("recruiterAdminListrecruiterAssignmentAcceptedSuccessfully")
            messages.success(request, message)
            return JsonResponse({"success": True, "message": message})

        except Organization.DoesNotExist:
            return JsonResponse({"success": False, "error": "employerNotFound."}, status=404)

        except User.DoesNotExist:
            return JsonResponse({"success": False, "error": "recruiterNotFound."}, status=404)

        except Exception as e:
            messages.error(request, f"anErrorOccurred_{str(e)}")
            return JsonResponse({"success": False, "error": f"anErrorOccurred_{str(e)}"}, status=500)

class RejectRecruiterView(View):
    def get(self, request, employer_id, recruiter_id, *args, **kwargs):
        try:
            employer_id = force_str(urlsafe_base64_decode(employer_id))
            recruiter_id = force_str(urlsafe_base64_decode(recruiter_id))

            employer = get_object_or_404(Organization, id=employer_id)
            recruiter = get_object_or_404(User, id=recruiter_id)

            message = _("recruiterAdminListRecruiterAssignmentRejectedSuccessfully")
            messages.success(request, message)
            return JsonResponse({"success": True, "message": message})

        except Organization.DoesNotExist:
            return JsonResponse({"success": False, "error": "employerNotFound."}, status=404)

        except User.DoesNotExist:
            return JsonResponse({"success": False, "error": "recruiterNotFound."}, status=404)

        except Exception as e:
            messages.error(request, f"anErrorOccurred_{str(e)}")
            return JsonResponse({"success": False, "error": f"anErrorOccurred_{str(e)}"}, status=500)


class RemoveWorkerFromAssignmentView(View):
    def get(self, request, *args, **kwargs):
        try:
            worker_id = kwargs.get('worker_id')
            assignment = get_object_or_404(WorkAssignment, worker__id=worker_id)
            work_request_id = assignment.work_request.pk  
            
            assignment.status = 'Deleted'
            assignment.save()

            messages.success(request, _("workersListWorkerAssignmentSuccessfullyMarkedAsDeleted"))
        
        except Exception as e:
            messages.error(request, f"errorRemovingWorker_{str(e)}")
            return redirect(reverse('recruiting_web:workrequest_list'))

        return redirect(reverse('recruiting_web:workrequest_detail', kwargs={'pk': work_request_id}))

@method_decorator(csrf_exempt, name='dispatch')
class UpdateStatusView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            work_requests = data.get('work_requests', [])
            status = data.get('status', '')
            
            if work_requests and status:
                updated_count = WorkRequests.objects.filter(id__in=work_requests).update(status=status)
                if updated_count > 0:
                    message = _("jobOrderDetailsWorkRequestsSuccessfullyUpdatedTo'{}'Status.").format(status)
                    messages.success(request, message)
                    return JsonResponse({'success': True, 'message': message})
                else:
                    message = _("jobOrderListNoWorkRequestsFoundToUpdate")
                    messages.error(request, message)
                    return JsonResponse({'success': False, 'message': message})
            message = _("jobOrderListInvalidDataProvided")
            messages.error(request, message)
            return JsonResponse({'success': False, 'message': message})

        except json.JSONDecodeError:
            message = _("jobOrderListInvalidJSONData")
            messages.error(request, message)
            return JsonResponse({'success': False, 'message': message})


class ContactWorkRequestsView(View):
    def get(self, request, contact_id):
        contact = get_object_or_404(User, id=contact_id)
        employer = contact.organizations.first()
        recruiters = EmployerRecruiter.objects.filter(employer=employer).select_related('recruiter')
        work_requests = WorkRequests.objects.filter(employer=employer)
        in_progress_work_requests = work_requests.filter(status__in=['Open', 'Requested'])
        closed_work_requests = work_requests.filter(status='Closed')
        draft_work_requests = work_requests.filter(status='Draft')

        context = {
            'contact': contact,
            'employer': employer,
            'in_progress_work_requests': in_progress_work_requests,
            'closed_work_requests': closed_work_requests,
            'draft_work_requests': draft_work_requests,
            'work_requests': work_requests,
            'recruiters': recruiters,
        }

        return render(request, 'recruiting/work_requests/workrequest_details.html', context)


@method_decorator(csrf_exempt, name='dispatch')
class AssignEmployerContactView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            employer_id = data.get("employer_id")
            user_id = data.get("user_id")

            if not employer_id or not user_id:
                return JsonResponse({
                    "success": False,
                    "error": _("employersEmployerIDAndUserIDAreRequired")
                }, status=400)

            employer = get_object_or_404(Organization, id=employer_id)
            user = get_object_or_404(User, id=user_id)

            if employer in user.organizations.all():
                return JsonResponse({
                    "success": False,
                    "error": _("employersUserIsAlreadyAssignedToThisOrganization")
                }, status=400)

            user.organizations.add(employer)

            return JsonResponse({
                "success": True,
                "message": _("employersOrganizationAssignedSuccessfullyToUser")
            })

        except json.JSONDecodeError:
            return JsonResponse({
                "success": False,
                "error": _("employersInvalidJSONPayload")
            }, status=400)
        except Exception as e:
            return JsonResponse({
                "success": False,
                "error": _("employersFailedToAssignOrganization: ") + str(e)
            }, status=500)

    def get(self, request, *args, **kwargs):
        return JsonResponse({
            "error": "GET not allowed."
        }, status=405)


@method_decorator(csrf_exempt, name='dispatch')
class AssignEmployersToRecruiterOrgView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            employer_ids = data.get('employer_org_id')
            recruiter_org_id = data.get('recruiter_org_id')

            if not employer_ids or not recruiter_org_id:
                return JsonResponse({
                    'success': False,
                    'message': 'Missing employer or recruiter organization ID.'
                })

            recruiter_org = get_object_or_404(
                Organization, id=recruiter_org_id, type='recruiter'
            )

            already_assigned = []
            newly_assigned = []

            for emp_id in employer_ids:
                employer_org = get_object_or_404(
                    Organization, id=emp_id, type='employer'
                )

                link, created = EmployerRecruiterOrgLink.objects.get_or_create(
                    employer_org=employer_org,
                    recruiter_org=recruiter_org,
                    defaults={
                        'employer_status': 'pending',
                        'recruiter_status': 'pending',
                        'final_status': 'pending'
                    }
                )

                if created:
                    newly_assigned.append(employer_org.name)
                    send_invitation_email_to_org(
                        employer_org, recruiter_org, request, role='employer'
                    )
                    send_invitation_email_to_org(
                        recruiter_org, employer_org, request, role='recruiter'
                    )
                else:
                    already_assigned.append(employer_org.name)

            if newly_assigned:
                messages.success(
                    request,
                    _("employersInvitationsCreated,EmailsSentSuccessfully,AndEmployer(s)AssignedToTheRecruiterOrganization")
                )

            if already_assigned:
                messages.warning(
                    request,
                    _("employersTheFollowingEmployersAre AlreadyAssigned: {}").format(', '.join(already_assigned))
                )

            return JsonResponse({
                'success': True,
                'newly_assigned': newly_assigned,
                'already_assigned': already_assigned,
                'message': "Processed employer assignment."
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            })

def get_response_status(receiver_org, other_org):
    try:
        link = EmployerRecruiterOrgLink.objects.get(
            employer_org=receiver_org if receiver_org.type == 'employer' else other_org,
            recruiter_org=receiver_org if receiver_org.type == 'recruiter' else other_org
        )
        return link.status
    except EmployerRecruiterOrgLink.DoesNotExist:
        return 'pending'


class InvitationResponseView(View):
    def get(self, request):
        action = request.GET.get('action')
        role = request.GET.get('role')
        receiver_org_id = request.GET.get('receiver_org_id')
        other_org_id = request.GET.get('other_org_id')

        try:
            receiver = get_object_or_404(Organization, id=receiver_org_id)
            other = get_object_or_404(Organization, id=other_org_id)

            if role == 'employer':
                employer_org = receiver
                recruiter_org = other
            else:
                employer_org = other
                recruiter_org = receiver

            link, _ = EmployerRecruiterOrgLink.objects.get_or_create(
                employer_org=employer_org,
                recruiter_org=recruiter_org
            )

            if role == 'employer':
                link.employer_status = action
            else:
                link.recruiter_status = action

            if link.is_fully_accepted() and link.final_status != 'accepted':
                link.final_status = 'accepted'
                send_invitation_to_primary_contacts(employer_org, recruiter_org, request)

            elif action == 'rejected':
                link.final_status = 'rejected'

            link.save()
            return render(request, "recruiting/emails/invitation_response.html")

        except Exception as e:
            return HttpResponse(f"Error: {str(e)}")


def send_invitation_email_to_org(receiver_org, other_org, request, role):
    """
    Sends initial invitation email to the org's notification email
    """
    protocol = 'https' if request.is_secure() else 'http'
    domain = request.get_host()

    accept_url = (
        f"{protocol}://{domain}/invitation-response/"
        f"?action=accepted&receiver_org_id={receiver_org.id}"
        f"&other_org_id={other_org.id}&role={role}"
    )
    reject_url = (
        f"{protocol}://{domain}/invitation-response/"
        f"?action=rejected&receiver_org_id={receiver_org.id}"
        f"&other_org_id={other_org.id}&role={role}"
    )

    subject = f"Invitation to collaborate with {other_org.name}"
    site_url = "https://test.okolabor.com"
    html_content = render_to_string("recruiting/emails/recruiter_invitation.html", {
        "receiver_org": receiver_org,
        "other_org": other_org,
        "accept_url": accept_url,
        "reject_url": reject_url,
        "site_url": site_url,
    })
    text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        to=[receiver_org.email],
    )
    email.attach_alternative(html_content, "text/html")
    email.send()


def send_invitation_to_primary_contacts(employer_org, recruiter_org, request):
    
    protocol = 'https' if request.is_secure() else 'http'
    domain = request.get_host()

    contacts = EmployerContact.objects.filter(employer=recruiter_org, is_primary=True)
    
    for contact in contacts:
        accept_url = f"{protocol}://{domain}/invitation-response/?action=accept&receiver_org_id={employer_org.id}&other_org_id={recruiter_org.id}&role=recruiter"
        reject_url = f"{protocol}://{domain}/invitation-response/?action=reject&receiver_org_id={employer_org.id}&other_org_id={recruiter_org.id}&role=recruiter"

        subject = f"Collaboration Confirmed with {recruiter_org.name}"
        message = f"""
Hi {contact.name},

Your organization '{employer_org.name}' has successfully established a collaboration with '{recruiter_org.name}'.

✅ Accept: {accept_url}  
❌ Reject: {reject_url}

Regards,  
Your Team
        """

        if contact.email:
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [contact.email],
                fail_silently=False
            )


def update_employer_recruiter_status(request):
    action = request.GET.get('action')
    employer_org_id = request.GET.get('employer_org_id')
    recruiter_org_id = request.GET.get('recruiter_org_id')
    primary_contact_id = request.GET.get('primary_contact_id')

    if not action or not employer_org_id or not recruiter_org_id or not primary_contact_id:
        return JsonResponse({'success': False, 'message': 'Invalid parameters'})

    employer_org = get_object_or_404(Organization, id=employer_org_id)
    recruiter_org = get_object_or_404(Organization, id=recruiter_org_id)
    primary_contact = get_object_or_404(EmployerContact, id=primary_contact_id)

    try:
        relation = EmployerRecruiterOrgLink.objects.get(
            employer_org=employer_org, recruiter_org=recruiter_org
        )

        if relation.status in ['accepted', 'rejected']:
            return JsonResponse({
                'success': False,
                'message': f'This assignment has already been {relation.status}.'
            })

        if action == 'accept':
            relation.status = 'accepted'
            msg = 'You have accepted the recruiter assignment.'
            subject = "Recruiter Assignment Accepted"
            message = f"Your organization '{employer_org.name}' has successfully accepted the assignment from '{recruiter_org.name}'."

        elif action == 'reject':
            relation.status = 'rejected'
            msg = 'You have rejected the recruiter assignment.'
            subject = "Recruiter Assignment Rejected"
            message = f"Your organization '{employer_org.name}' has rejected the assignment from '{recruiter_org.name}'."

        else:
            return JsonResponse({'success': False, 'message': 'Invalid action.'})

        relation.user_updated_by = primary_contact
        relation.save()

        send_mail(subject, message, settings.EMAIL_HOST_USER, [primary_contact.email])
        messages.success(request, msg)

        return JsonResponse({'success': True, 'message': msg})

    except EmployerRecruiterOrgLink.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'No relationship found'})


class EmployerRecruiterOrgStatusListView(ListView):
    model = EmployerRecruiterOrgLink
    template_name = 'recruiting/relationship/recruiter_status_list.html'
    context_object_name = 'links'

    def get_queryset(self):
        return EmployerRecruiterOrgLink.objects.filter(
            final_status__in=['accepted', 'rejected', 'pending']
        ).select_related(
            'employer_org',
            'recruiter_org',
            'user_updated_by__user'
        )
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
            {'name': _('recruiterStatusHome'), 'url': reverse_lazy('index')},
            {'name': _('recruiterStatusRecruiterStatusList'), 'url': None},
        ]
        return context

class EmployerRecruiterOrgLinkDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        link = get_object_or_404(EmployerRecruiterOrgLink, pk=pk, deleted=False)

        if request.user.groups.filter(name='admin').exists():
            link_str = str(link)
            link.delete(user=request.user)
            messages.success(request, _('employersLink "%(link_str)s" deleted successfully.') % {'link_str': link_str})

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'})

            return redirect('recruiting_web:recruiter-status-list')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'forbidden'}, status=403)

            return HttpResponseForbidden(_("employersYouDoNotHavePermissionToDeleteThisLink"))


class SummaryViews(View):
    def get(self, request, pk, role_id):
        work_assign_form = WorkerAssignmentForm()
        form = FilterWorkExperienceForm()
        filter_form = AdvancedFilterForm()

        tab = request.GET.get('tab', 'shortlist')

        work_request = get_object_or_404(WorkRequests, pk=pk)
        role = get_object_or_404(Role, pk=role_id)
        work_requests = WorkRequests.objects.filter(status='Open').prefetch_related('roles')

        
        workers = User.objects.filter(groups__name='worker').distinct().order_by('-created_at')

        worker_data = []
        for worker in workers:
            profile_completion = calculate_profile_completion(worker)
            worker_details = get_worker_preferences(worker)
            worker.profile_completion_percentage = profile_completion

            latest_assignment = WorkAssignment.objects.filter(
                worker=worker, work_request=work_request, role=role
            ).order_by('-assigned_date').first()
            worker.latest_status = latest_assignment.status if latest_assignment else "No Assignment"

            for key, value in worker_details.items():
                setattr(worker, key, value)

            worker_data.append({
                'id': worker.id,
                'firstname': worker.first_name,
                'lastname': worker.last_name,
                'email': worker.email,
                'profile_completion': profile_completion,
                **worker_details
            })

        shortlisted_workers_data = []
        offersent_workers_data = []
        confirmed_workers_data = []

        all_assignments = {
            'shortlist': get_shortlisted_workers(status='assigned', role_id=role_id),
            'offersent': get_shortlisted_workers(status='offersent', role_id=role_id),
            'confirmed': get_shortlisted_workers(status='confirmed', role_id=role_id),
        }

        for status_key, assignments in all_assignments.items():
            unique_ids = set()
            target_list = []
            for assignment in assignments:
                worker = assignment.worker
                if worker.id not in unique_ids:
                    unique_ids.add(worker.id)
                    profile_completion = calculate_profile_completion(worker)
                    worker_details = get_worker_preferences(worker)

                    target_list.append({
                        'id': worker.id,
                        'firstname': worker.first_name,
                        'lastname': worker.last_name,
                        'email': worker.email,
                        'town': worker_details.get('town', 'Not Provided'),
                        'profile_completion': profile_completion,
                        'work_experience': worker_details.get('work_experience', 'Not Provided'),
                        'english_proficiency': worker_details.get('english_proficiency', 'Not Provided'),
                        'location_preference': worker_details.get('location_preference', 'Not Provided'),
                        'status': assignment.status,
                    })

            if status_key == 'shortlist':
                shortlisted_workers_data = target_list
            elif status_key == 'offersent':
                offersent_workers_data = target_list
            elif status_key == 'confirmed':
                confirmed_workers_data = target_list

        shortlisted_count = len(shortlisted_workers_data)
        offersent_count = len(offersent_workers_data)
        confirmed_count = len(confirmed_workers_data)

        context = {
            'workers': worker_data,
            'work_requests': work_requests,
            'form': form,
            'work_assign_form': work_assign_form,
            'filter_form': filter_form,
            'role': role,
            'work_request': work_request,
            'shortlisted_workers': shortlisted_workers_data,
            'offersent_workers': offersent_workers_data,
            'confirmed_workers': confirmed_workers_data,
            'shortlisted_count': shortlisted_count,
            'offersent_count': offersent_count,
            'confirmed_count': confirmed_count,
            'count': len(shortlisted_workers_data if tab == 'shortlist' else offersent_workers_data if tab == 'offersent' else confirmed_workers_data),
            'tab': tab,
        }

        return render(request, 'recruiting/work_requests/summaryList/summarylist.html', context)


class EditEmploymentLocationView(View):
    def post(self, request, pk):
        location = get_object_or_404(EmploymentLocation, pk=pk)
        form = RoleEmploymentLocationForm(request.POST, instance=location)
        if form.is_valid():
            form.save()
            messages.success(request, _('roleEmploymentLocationEmploymentLocationUpdatedSuccessfully'))
            return redirect(f'{reverse("recruiting_web:workrequest_detail", args=[location.role.work_request.pk])}?open_role={location.role.id}')
        else:
            messages.error(request, _('roleEmploymentLocationThereWasAnErrorUpdatingTheEmploymentLocation'))


class DeleteEmploymentLocationView(View):
    def post(self, request, pk):
        location = get_object_or_404(EmploymentLocation, pk=pk)
        try:
            location.delete()
            messages.success(request, _('roleEmploymentLocationEmploymentLocationDeletedSuccessfully'))
            return redirect(f'{reverse("recruiting_web:workrequest_detail", args=[location.role.work_request.pk])}?open_role={location.role.id}')
        except Exception as e:
            messages.error(request, _('roleEmploymentLocationErrorDeletingEmploymentLocation: %(error)s') % {'error': str(e)})


class EditHousingInformationView(View):
    def post(self, request, pk):
        housing = get_object_or_404(HousingInformation, pk=pk)
        form = RoleHousingInformationForm(request.POST, instance=housing)
        if form.is_valid():
            form.save()
            messages.success(request, _('joDetailsHousingInfoHousingInformationUpdatedSuccessfully'))
            return redirect(f'{reverse("recruiting_web:workrequest_detail", args=[housing.role.work_request.pk])}?open_role={housing.role.id}')
        else:
            messages.error(request, _('joDetailsHousingInfoThereWasAnErrorUpdatingTheHousingInformation'))
            return redirect(f'{reverse("recruiting_web:workrequest_detail", args=[housing.role.work_request.pk])}?open_role={housing.role.id}')


class DeleteHousingInformationView(View):
    def post(self, request, pk):
        housing = get_object_or_404(HousingInformation, pk=pk)
        try:
            work_request_pk = housing.role.work_request.pk
            housing.delete()
            messages.success(request, _('joDetailsHousingInfoHousingInformationDeletedSuccessfully'))
            return redirect(f'{reverse("recruiting_web:workrequest_detail", args=[work_request_pk])}?open_role={housing.role.id}')
        except Exception as e:
            messages.error(request, _('joDetailsHousingInfoErrorDeletingHousingInformation: %(error)s') % {'error': str(e)})
            return redirect(f'{reverse("recruiting_web:workrequest_detail", args=[housing.role.work_request.pk])}?open_role={housing.role.id}')

class EditMealProvisionView(View):
    def post(self, request, pk):
        meal_provision = get_object_or_404(MealProvision, pk=pk)
        form = RoleMealProvision(request.POST, instance=meal_provision)

        if form.is_valid():
            form.save()
            messages.success(request, _('joDetailsMealsMealProvisionUpdatedSuccessfully'))
            return redirect(f'{reverse("recruiting_web:workrequest_detail", args=[meal_provision.role.work_request.pk])}?open_role={meal_provision.role.id}')
        else:
            messages.error(request, _('joDetailsMealsThereWasAnErrorUpdatingTheMealProvision'))
            return redirect(f'{reverse("recruiting_web:workrequest_detail", args=[meal_provision.role.work_request.pk])}?open_role={meal_provision.role.id}')


class DeleteMealProvisionView(View):
    def post(self, request, pk):
        meal_provision = get_object_or_404(MealProvision, pk=pk)
        try:
            work_request_pk = meal_provision.role.work_request.pk
            meal_provision.delete()
            messages.success(request, _('joDetailsMealsMealProvisionDeletedSuccessfully'))
            return redirect(f'{reverse("recruiting_web:workrequest_detail", args=[work_request_pk])}?open_role={meal_provision.role.id}')
        except Exception as e:
            messages.error(request, _('joDetailsMealsErrorDeletingMealProvision: %(error)s') % {'error': str(e)})
            return redirect(f'{reverse("recruiting_web:workrequest_detail", args=[meal_provision.role.work_request.pk])}?open_role={meal_provision.role.id}')


class EditRoleHoursView(View):
    def post(self, request, pk):
        hours = get_object_or_404(Hours, pk=pk)
        form = RoleHoursForm(request.POST, instance=hours)

        work_request_id = request.POST.get('work_request_id', None)

        if form.is_valid():
            form.save()
            messages.success(request, _('joDetailsHoursHoursUpdatedSuccessfully'))
        else:
            messages.error(request, _('joDetailsHoursThereWasAnErrorUpdatingTheHours'))

        if work_request_id:
            return redirect(f'{reverse("recruiting_web:workrequest_detail", args=[work_request_id])}?open_role={hours.role.id}')
        else:
            return redirect('/')

class DeleteRoleHoursView(View):
    def post(self, request, pk):
        hours = get_object_or_404(Hours, pk=pk)
        work_request_id = request.POST.get('work_request_id', None)

        try:
            hours.delete()
            messages.success(request, _('joDetailsHoursHoursDeletedSuccessfully'))
        except Exception as e:
            messages.error(request, _('joDetailsHoursErrorDeletingHours: %(error)s')% {'error': str(e)})

        if work_request_id:
            return redirect(f'{reverse("recruiting_web:workrequest_detail", args=[work_request_id])}?open_role={hours.role.id}')
        else:
            return redirect('/')
class EditRoleWagesView(View):
    def post(self, request, pk):
        wages = get_object_or_404(Wages, pk=pk)
        form = RoleWagesForm(request.POST, instance=wages)

        work_request_id = request.POST.get('work_request_id', wages.role.work_request.id)

        if form.is_valid():
            form.save()
            messages.success(request, _('joDetailsWagesWagesUpdatedSuccessfully'))
        else:
            messages.error(request, _('joDetailsWagesThereWasAnErrorUpdatingTheWages'))

        if work_request_id:
            return redirect(f'{reverse("recruiting_web:workrequest_detail", args=[work_request_id])}?open_role={wages.role.id}')
        else:
            return redirect('/')

class DeleteRoleWagesView(View):
    def post(self, request, pk):
        wages = get_object_or_404(Wages, pk=pk)
        wages.deleted_at = timezone.now()
        wages.save()
        messages.success(request, _("joDetailsWagesWagesDeletedSuccessfully"))
        return redirect(f'{reverse("recruiting_web:workrequest_detail", args=[wages.role.work_request.id])}?open_role={wages.role.id}')

class EditRoleQualificationView(View):
    def post(self, request, pk):
        qualification = get_object_or_404(Qualification, pk=pk)
        form = RoleQualificationForm(request.POST, instance=qualification)

        work_request_id = request.POST.get('work_request_id', None)

        if form.is_valid():
            form.save()
            messages.success(request, _('joDetailsQualificationsQualificationUpdatedSuccessfully'))
            return redirect(f'{reverse("recruiting_web:workrequest_detail", args=[qualification.role.work_request.pk])}?open_role={qualification.role.id}')
        else:
            messages.error(request, _('joDetailsQualificationsThereWasAnErrorUpdatingTheQualification'))


class DeleteQualificationView(View):
    def post(self, request, pk):
        qualification = get_object_or_404(Qualification, pk=pk)
        qualification.delete()

        messages.success(request, _("joDetailsQualificationsQualificationDeletedSuccessfully"))
        return redirect(f'{reverse("recruiting_web:workrequest_detail", args=[qualification.role.work_request.pk])}?open_role={qualification.role.id}')

class DeleteDeductionView(View):
    def post(self, request, pk):
        deduction = get_object_or_404(Deduction, pk=pk)
        try:
            deduction.delete()
            messages.success(request, 'DeductionDeletedSuccessfully.')
            return redirect(f'{reverse("recruiting_web:workrequest_detail", args=[deduction.role.work_request.pk])}?open_role={deduction.role.id}')

        except Exception as e:
            messages.error(request, f'ErrorDeletingDeduction: {str(e)}')


class DeductionEditView(View):
    def post(self, request, deduction_id):
        deduction = get_object_or_404(Deduction, id=deduction_id)

        data = {
            'role': request.POST.get('role'),
            'description': request.POST.get('description'),
            'deduction_amount': request.POST.get('deduction_amount'),
            'frequency_of_pay': request.POST.get('frequency_of_pay'),
        }
        form = RoleDeductionForm(data, instance=deduction)
        if form.is_valid():
            form.save()
            messages.success(request, "Deduction updated successfully.")
            return redirect(f'{reverse("recruiting_web:workrequest_detail", args=[deduction.role.work_request.pk])}?open_role={deduction.role.id}')
        else:
            return redirect(f'{reverse("recruiting_web:workrequest_detail", args=[deduction.role.work_request.pk])}?open_role={deduction.role.id}')
