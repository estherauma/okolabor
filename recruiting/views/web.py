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
from django.utils.decorators import method_decorator
from django.contrib.auth.models import Group
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.http import HttpResponseRedirect,HttpResponseForbidden
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from collections import defaultdict
from django.db.models import Count
from datetime import date
from django.template.loader import render_to_string
import os
from recruiting.utils import get_worker_preferences, calculate_profile_completion
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
    RoleEmploymentLocationForm
)
from theme.forms import (
    FilterWorkExperienceForm,
    AdvancedFilterForm,
    DynamicWorkExperienceForm
)
from account.models import UserPreference
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

    
class EmployerListView(View):
    def get(self, request):
        user = request.user
        query = request.GET.get('query')

        if user.groups.filter(name='admin').exists():
            employers_list = Organization.objects.filter(type='employer')

        elif user.groups.filter(name='recruiter').exists():
            recruiter_orgs = Organization.objects.filter(
                type='recruiter',
                recruiters=user
            ).distinct()

            assigned_links = EmployerRecruiterOrgLink.objects.filter(
                recruiter_org__in=recruiter_orgs
            )

            assigned_employer_ids = assigned_links.values_list('employer_org__id', flat=True)
            employers_list = Organization.objects.filter(
                id__in=assigned_employer_ids,
                type='employer'
            ).distinct()

        else:
            employers_list = Organization.objects.none()

        if query:
            employers_list = employers_list.filter(
                Q(name__icontains=query) |
                Q(email__icontains=query) |
                Q(address__icontains=query) |
                Q(country__icontains=query) |
                Q(phone__icontains=query)
            )

        paginator = Paginator(employers_list, len(employers_list) if employers_list.exists() else 1)
        page_number = request.GET.get('page')
        employers = paginator.get_page(page_number)

        recruiter_organizations = Organization.objects.filter(type='recruiter')

        employers_data = []
        for employer in employers:
            assigned_links = EmployerRecruiterOrgLink.objects.filter(employer_org=employer)

            recruiter_org_names = list(set(
                link.recruiter_org.name for link in assigned_links
            ))

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

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'employers': employers_data,
                'has_more': employers.has_next()
            })

        context = {
            'employers': employers_data,
            'query': query,
            'recruiters': recruiter_organizations
        }
        return render(request, 'recruiting/employers/list.html', context)

        
class EmployerDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        user = request.user
        employer = get_object_or_404(Organization, pk=pk, type='employer', deleted=False)


        if user.groups.filter(name='admin').exists():
            employer_name = employer.name
            employer.delete(user=user)
            
            messages.success(request, _('Employer "%(employer_name)s" DeletedSuccessfully.') % {'employer_name': employer_name})
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'})
            return redirect('recruiting_web:employer_list')

        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'forbidden'}, status=403)
            return HttpResponseForbidden(_("youDoNotHavePermissionToDeleteThisEmployer."))

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

            messages.success(request, _('Employer "%(employer_name)s" Edited Successfully.') % {'employer_name': employer.name})
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'})
            return redirect('recruiting_web:employer_list')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'forbidden'}, status=403)
            return HttpResponseForbidden(_("You do not have permission to edit this employer."))

class RecruiterListViewInAdmin(View):
    def get(self, request):
        user = request.user
        query = request.GET.get('query')

        if user.groups.filter(name='admin').exists():
            recruiters_list = Organization.objects.filter(type='recruiter')
        else:
            recruiters_list = Organization.objects.none()

        if query:
            recruiters_list = recruiters_list.filter(
                Q(name__icontains=query) |
                Q(email__icontains=query) |
                Q(address__icontains=query) |
                Q(city__icontains=query) |
                Q(country__icontains=query) |
                Q(phone__icontains=query)
            )

        paginator = Paginator(recruiters_list, len(recruiters_list)) 
        page_number = request.GET.get('page')
        recruiters = paginator.get_page(page_number)

        recruiters_data = []
        for recruiter in recruiters:
            assigned_links = EmployerRecruiterOrgLink.objects.filter(recruiter_org=recruiter)
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

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'recruiters': recruiters_data,
                'has_more': recruiters.has_next()
            })

        context = {'recruiters': recruiters_data, 'query': query}
        return render(request, 'recruiting/recruiters_list/list.html', context)


class RecruiterDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        user = request.user
        recruiter = get_object_or_404(Organization, pk=pk, type='recruiter',deleted=False)

        if user.groups.filter(name='admin').exists():
            recruiter_name = recruiter.name
            recruiter.delete(user=user)
            messages.success(request, _('Recruiter "%(recruiter_name)s" deletedSuccessfully.') % {'recruiter_name': recruiter_name})
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'})
            return redirect('recruiting_web:recruiter_admin_list')

        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'forbidden'}, status=403)
            return HttpResponseForbidden(_("youDoNotHavePermissionToDeleteThisRecruiter."))

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

            messages.success(request, _('Recruiter "%(recruiter_name)s" editedSuccessfully.') % {'recruiter_name': recruiter.name})
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'})
            return redirect('recruiting_web:recruiter_admin_list')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'forbidden'}, status=403)
            return HttpResponseForbidden(_("You do not have permission to edit this recruiter."))

class EmployerCreateView(CreateView):
    model = Organization
    form_class = EmployerForm
    template_name = 'recruiting/employers/create.html'

    def form_valid(self, form):
        messages.success(self.request, _('addEmployerEmployerCreatedSuccessfully'))
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
        user = request.user
        employer = get_object_or_404(Organization, pk=pk)

        work_requests = WorkRequests.objects.filter(employer=employer)

        in_progress_work_requests = work_requests.filter(status__in=['Open', 'Requested'])
        closed_work_requests = work_requests.filter(status='Closed')
        draft_work_requests = work_requests.filter(status='Draft')

        recruiters = EmployerRecruiter.objects.filter(employer=employer).select_related('recruiter')
        contacts = employer.contacts.all()

        assigned_organizations = Organization.objects.filter(
            assigned_employer_orgs__employer_org=employer
        ).distinct()

        assigned_orgs_data = []
        for org in assigned_organizations:
            assigned_recruiters = EmployerRecruiter.objects.filter(employer=employer)
            recruiter_names = list(set(
                rec.recruiter.get_full_name()
                for rec in assigned_recruiters
                if user.groups.filter(name='admin').exists() or rec.recruiter == user
            ))
            
            assigned_orgs_data.append({
                'id': org.id,
                'name': org.name,
                'email': org.email,
                'address': org.address,
                'country': org.country,
                'phone': org.phone,
                'recruiters': recruiter_names
            })
        context = {
            'employer': employer,
            'in_progress_work_requests': in_progress_work_requests,
            'closed_work_requests': closed_work_requests,
            'draft_work_requests': draft_work_requests,
            'recruiters': recruiters,
            'contacts': contacts,
            'work_requests': work_requests,
            'assigned_organizations': assigned_orgs_data
        }
        return render(request, 'recruiting/employers/detail.html', context)
    

class RecruiterDetailView(View):
    def get(self, request, pk):
        user = request.user
        recruiter_org = get_object_or_404(Organization, pk=pk, type='recruiter')

        assigned_links = EmployerRecruiterOrgLink.objects.filter(recruiter_org=recruiter_org)
        employer_orgs = Organization.objects.filter(
            id__in=assigned_links.values_list('employer_org__id', flat=True)
        ).distinct()

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

        contacts = recruiter_org.contacts.all()

        context = {
            'employer': recruiter_org,
            'employer_organizations': employer_orgs_data,
            'in_progress_work_requests': in_progress_work_requests,
            'closed_work_requests': closed_work_requests,
            'draft_work_requests': draft_work_requests,
            'contacts': contacts,
            'work_requests': work_requests
        }
        return render(request, 'recruiting/recruiters_list/workrequest_detail.html', context)

class WorkRequestsListView(View):
    def get(self, request):
        user = request.user
        admin_group = Group.objects.get(name='admin')
        recruiter_group = Group.objects.get(name='recruiter')

        if admin_group in user.groups.all():
            work_requests = WorkRequests.objects.all()

        elif recruiter_group in user.groups.all():
            user_orgs = user.organizations.all()
            if user_orgs.exists():
                user_org = user_orgs.first() 
                assigned_employer_ids = EmployerRecruiterOrgLink.objects.filter(
                    recruiter_org=user_org
                ).values_list("employer_org_id", flat=True)

                work_requests = WorkRequests.objects.filter(employer_id__in=assigned_employer_ids)
            else:
                work_requests = WorkRequests.objects.none()
        else:
            work_requests = WorkRequests.objects.none()

        # Attach recruiter_org to each work request
        for wr in work_requests:
            recruiter_link = EmployerRecruiterOrgLink.objects.filter(employer_org=wr.employer).first()
            wr.recruiter_org = recruiter_link.recruiter_org if recruiter_link else None

        context = {
            "work_requests": work_requests,
            "employers": Organization.objects.filter(type='employer'),
            "recruiter": Organization.objects.filter(type='recruiter'),
        }
        return render(request, "recruiting/work_requests/list.html", context)


class DeleteAssignedOrganizationView(View):
    def post(self, request, employer_id, recruiter_org_id):
        employer = get_object_or_404(Organization, pk=employer_id)
        recruiter_org = get_object_or_404(Organization, pk=recruiter_org_id)

        # Delete the assignment link between employer and recruiter organization
        EmployerRecruiterOrgLink.objects.filter(
            employer_org=employer,
            recruiter_org=recruiter_org
        ).delete()
        messages.success(self.request, _('employerRecruiterDeletedSuccessfully'))
        return redirect('recruiting_web:employer_detail', pk=employer.id)



class DeleteEmployerOrganizationFromRecruiterView(View):
    def post(self, request, recruiter_org_id, employer_org_id):
        recruiter_org = get_object_or_404(Organization, pk=recruiter_org_id, type='recruiter')
        employer_org = get_object_or_404(Organization, pk=employer_org_id)

        # Delete the link between recruiter and employer
        EmployerRecruiterOrgLink.objects.filter(
            recruiter_org=recruiter_org,
            employer_org=employer_org
        ).delete()
        messages.success(self.request, _('employerRecruiterDeletedSuccessfully'))

        return redirect('recruiting_web:recruiter_org_detail', pk=recruiter_org.id)



class WorkRequestCreateView(CreateView):
    model = WorkRequests
    form_class = WorkRequestForm
    template_name = 'recruiting/work_requests/create.html'

    def form_valid(self, form):
        messages.success(self.request, _('createJobOrderJobOrderCreatedSuccessfully'))
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

class WorkRequestEditView(LoginRequiredMixin, View):
    def post(self, request, pk):
        work_request = get_object_or_404(WorkRequests, pk=pk)
        form = WorkRequestForm(request.POST, instance=work_request)
        if form.is_valid():
            form.save()
            messages.success(request, _('WorkRequestEditedSuccessfully'))
            return redirect('recruiting_web:workrequest_detail', pk=work_request.pk)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
            return redirect('recruiting_web:workrequest_list')
        
class WorkRequestDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        user = request.user
        work_request = get_object_or_404(WorkRequests, pk=pk,deleted=False)

        if user.groups.filter(name='admin').exists():
            work_request_name = work_request.name
            work_request.delete(user=user)
            messages.success(request, _('WorkRequest "%(work_request_name)s" Deleted Successfully.') % {'work_request_name': work_request_name})
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'})
            return redirect('recruiting_web:workrequest_list')
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'forbidden'}, status=403)
            return HttpResponseForbidden(_("You do not have permission to delete this work request."))



class AddWorkersWorkRequests(View):
    def get(self, request, pk, role_id):
        work_assign_form = WorkerAssignmentForm()
        form = DynamicWorkExperienceForm(request.GET or None)
        filter_form = AdvancedFilterForm(request.GET or None)
        search_query = request.GET.get('search', '')
        page_number = request.GET.get('page', 1)
        per_page = request.GET.get('per_page', 25)

        try:
            per_page = int(per_page)
        except ValueError:
            per_page = 4  # Fallback default

        work_request = get_object_or_404(WorkRequests, pk=pk)
        role = get_object_or_404(Role, pk=role_id)
        work_requests = WorkRequests.objects.filter(status='Open').prefetch_related('roles')

        # Retrieve the state from the session
        session_key = f'role_{role_id}_state'
        if session_key in request.session:
            state = request.session[session_key]
            search_query = state.get('search_query', '')
            page_number = state.get('page_number', 1)
            per_page = state.get('per_page', 25)

        # Get all workers (not filtered by role)
        workers = User.objects.filter(
            groups__name='worker'
        ).distinct().order_by('-created_at')

        if search_query:
            workers = workers.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query)
            )
        # 🔍 Experience Filters
        type_sector = request.GET.get('type_sector')
        dynamic_field_1 = request.GET.get('dynamic_field_1')
        dynamic_field_2 = request.GET.get('dynamic_field_2')


        if type_sector:
            workers = workers.filter(
                crop_experiences__job_type__iexact=type_sector
            )

        if dynamic_field_1 and dynamic_field_1.strip():
            workers = workers.filter(
                crop_experiences__type_details__iexact=dynamic_field_1
            )

        if dynamic_field_2 and dynamic_field_2.strip():
            workers = workers.filter(
                crop_experiences__job_experience_details__value__iexact=dynamic_field_2
            )

        # 🔍 Advanced Filter Form (from UserPreference model)
        if filter_form.is_valid():
            for field_name, value in filter_form.cleaned_data.items():
                if value is not None and str(value).strip() != '':
                    if field_name == 'availability' and isinstance(value, date):
                        workers = workers.filter(
                            userpreference__key='availability',
                            userpreference__value__gte=value.strftime('%Y-%m-%d')
                        )
                    else:
                        workers = workers.filter(
                            userpreference__key=field_name,
                            userpreference__value__iexact=value
                        )
        workers = workers.distinct()

        paginator = Paginator(workers, per_page)
        page_obj = paginator.get_page(page_number)

        worker_data = []
        for worker in page_obj:
            profile_completion = calculate_profile_completion(worker)
            worker_details = get_worker_preferences(worker)

            worker.profile_completion_percentage = profile_completion
            latest_assignment = WorkAssignment.objects.filter(
                worker=worker,
                work_request=work_request,
                role=role
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

        # Retrieve shortlisted workers based on status and role
        shortlisted_workers = get_shortlisted_workers(status='assigned', role_id=role_id)
        offersent_workers = get_shortlisted_workers(status='offersent', role_id=role_id)
        confirmed_workers = get_shortlisted_workers(status='confirmed', role_id=role_id)
        cancel_workers = get_shortlisted_workers(status='cancelled', role_id=role_id)

        shortlisted_workers_data = []
        for assignment in shortlisted_workers:
            worker = assignment.worker
            profile_completion = calculate_profile_completion(worker)
            worker_details = get_worker_preferences(worker)
            shortlisted_workers_data.append({
                'id': worker.id,
                'firstname': worker.first_name,
                'lastname': worker.last_name,
                'email': worker.email,
                'profile_completion': profile_completion,
                'status': assignment.status,
                **worker_details
            })

        offersent_workers_data = []
        for assignment in offersent_workers:
            worker = assignment.worker
            profile_completion = calculate_profile_completion(worker)
            worker_details = get_worker_preferences(worker)
            offersent_workers_data.append({
                'id': worker.id,
                'firstname': worker.first_name,
                'lastname': worker.last_name,
                'email': worker.email,
                'profile_completion': profile_completion,
                'status': assignment.status,
                **worker_details
            })

        confirmed_workers_data = []
        for assignment in confirmed_workers:
            worker = assignment.worker
            profile_completion = calculate_profile_completion(worker)
            worker_details = get_worker_preferences(worker)
            confirmed_workers_data.append({
                'id': worker.id,
                'firstname': worker.first_name,
                'lastname': worker.last_name,
                'email': worker.email,
                'profile_completion': profile_completion,
                'status': assignment.status,
                **worker_details
            })

        cancelled_workers_data = []
        unique_cancelled_workers = set()
        for assignment in cancel_workers:
            worker = assignment.worker
            if worker.id not in unique_cancelled_workers:
                unique_cancelled_workers.add(worker.id)
                profile_completion = calculate_profile_completion(worker)
                worker_details = get_worker_preferences(worker)
                cancelled_workers_data.append({
                    'id': worker.id,
                    'firstname': worker.first_name,
                    'lastname': worker.last_name,
                    'email': worker.email,
                    'profile_completion': profile_completion,
                    'status': assignment.status,
                    **worker_details
                })

        shortlisted_count = len(shortlisted_workers_data)
        offersent_count = len(offersent_workers_data)
        confirmed_count = len(confirmed_workers_data)
        cancelled_count = len(cancelled_workers_data)

        # Store the state in the session
        request.session[session_key] = {
            'search_query': search_query,
            'page_number': page_number,
            'per_page': per_page,
        }

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'workers': worker_data, 'num_pages': paginator.num_pages})
        

        context = {
            'workers': page_obj,  # All workers (not role-specific)
            'work_requests': WorkRequests.objects.filter(status='Open').prefetch_related('roles'),
            'form': form,
            'work_assign_form': work_assign_form,
            'filter_form': filter_form,
            'search_query': search_query,
            'paginator': paginator,
            'per_page': per_page,
            'role': role,
            'work_request': work_request,
            'shortlisted_workers': shortlisted_workers_data,
            'offersent_workers': offersent_workers_data,
            'confirmed_workers': confirmed_workers_data,
            'cancelled_workers': cancelled_workers_data,
            'shortlisted_count': shortlisted_count,
            'offersent_count': offersent_count,
            'confirmed_count': confirmed_count,
            'cancelled_count': cancelled_count,
        }
        return render(request, 'recruiting/work_requests/create_addworker.html', context)

@method_decorator(require_POST, name='dispatch')
class CopyWorkersView(View):
    def post(self, request):
        worker_ids = request.POST.getlist('worker_ids[]')
        work_request_id = request.POST.get('work_request')
        role_id = request.POST.get('role')
        status = request.POST.get('status', 'Assigned')

        if not worker_ids or not work_request_id or not role_id:
            messages.error(request, _('Invalid request, missing data'))
            return JsonResponse({'error': _('Invalid request, missing data')}, status=400)

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

            messages.success(request, _('workersAssignedSuccessfully!'))
            return JsonResponse({'success': _('Workers assigned successfully!')})
        
        except Exception as e:
            messages.error(request, _('anErrorOccurred: ') + str(e))
            return JsonResponse({'error': _('An error occurred: ') + str(e)}, status=500)

class GetRolesView(View):
    def get(self, request, *args, **kwargs):
        work_request_id = request.GET.get('work_request_id')
        if not work_request_id:
            return JsonResponse({'error': 'Work request ID is required'}, status=400)

        try:
            # Fetch the work request with related roles using prefetch_related
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
        WorkAssignment.objects.filter(worker_id__in=worker_ids, status='assigned').update(status='offersent')
        messages.success(request, _("offerSentSuccessfully."))
        return JsonResponse({'status':'success','success': 'True', 'message': 'Offer sent successfully.'})

@method_decorator(csrf_exempt, name='dispatch')
class CancelOfferView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        worker_ids = data.get('worker_ids', [])
        WorkAssignment.objects.filter(worker_id__in=worker_ids, status='offersent').update(status='cancelled')
        messages.success(request, _("OfferCancelledSuccessfully."))
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
            messages.success(request, "workersAddedToShortlistSuccessfully.")
            return JsonResponse({'success': True, 'message': _("workersAddedToShortlistSuccessfully.")})
        else:
            messages.warning(request, "someWorkersAreAlreadyShortlisted.")
            return JsonResponse({'success': False, 'message': _("someWorkersAreAlreadyShortlisted.")})


class ShowWorkerDetails(View):
    def get(self, request, pk):
        view = WorkerDetailsView()
        return view.get(request, pk)


class WorkRequestDetailView(View):
    def get(self, request, pk):
        work_request = get_object_or_404(WorkRequests, pk=pk)
        

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

        roles_qs = work_request.roles.filter(deleted_at__isnull=True)

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

        print(role_housing_information_forms,"role_housing_information_forms")
        context = {
            'workrequest': work_request,
            'roles': roles_qs,
            'role_forms': role_forms,
            'worker_summary': worker_summary,
            'total_shortlist_count': total_shortlist_count,
            'total_offersent_count': total_offersent_count,
            'total_confirmed_count': total_confirmed_count,
            'role_information_forms': role_information_forms,
            'role_housing_information_forms': role_housing_information_forms
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
    
class EditRoleView(View):
    def post(self, request, pk):
        role = get_object_or_404(Role, pk=pk)
        form = WorkRequestRoleForm(request.POST, instance=role)
        if form.is_valid():       
            form.save()
            messages.success(request, 'Role updated successfully.')
            return redirect('recruiting_web:workrequest_detail', pk=role.work_request.pk)
        else:
            return redirect('recruiting_web:workrequest_detail', pk=role.work_request.pk)
        
class DeleteRoleView(View):
    def post(self, request, pk):
        role = get_object_or_404(Role, pk=pk)
        work_request_pk = role.work_request.pk 
        role.delete(user=request.user)
        messages.success(request, 'Role deleted successfully.')
        return redirect('recruiting_web:workrequest_detail', pk=work_request_pk)

class RecruiterListView(LoginRequiredMixin, View):
    def get(self, request):
        if not request.user.groups.filter(name='recruiter_admin').exists():
            return redirect('recruiting_web:access_denied')

        recruiters = User.objects.filter(groups__name='recruiter').prefetch_related('employerrecruiter_set__employer')
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
            messages.success(request, _("Recruiter {email} assigned to {employer}.").format(email=recruiter.email, employer=employer.name))
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
        message = get_object_or_404(OkoMessage, pk=id)
        context = {'message': message}
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

            messages.success(request, _("recruiterAssignmentAcceptedSuccessfully."))
            return JsonResponse({"success": True, "message": "recruiterAssignmentAcceptedSuccessfully."})

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


            messages.success(request, _("recruiterAssignmentRejectedSuccessfully."))
            return JsonResponse({"success": True, "message": "recruiterAssignmentRejectedSuccessfully."})

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

            messages.success(request, _("WorkerAssignmentSuccessfullyMarkedAsDeleted."))
        
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
                    messages.success(request, _("updateWorkRequestsSuccessfullyUpdatedTo'{}'Status.").format(status))
                    return JsonResponse({'success': True, 'message': f"workRequestsSuccessfullyUpdatedTo'{status}'Status."})
                else:
                    messages.error(request, _("noWorkRequestsFoundToUpdate."))
                    return JsonResponse({'success': False, 'message': 'noWorkRequestsFoundtoUpdate.'})
            messages.error(request, _("invalidDataProvided."))
            return JsonResponse({'success': False, 'message': 'invalidDataProvided.'})

        except json.JSONDecodeError:
            messages.error(request, "invalidJSONData.")
            return JsonResponse({'success': False, 'message': 'invalidJSONData.'})


class ContactWorkRequestsView(View):
    def get(self, request, contact_id):
        contact = get_object_or_404(EmployerContact, id=contact_id)
        employer = contact.employer 
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
            name = data.get("name")
            email = data.get("email")
            phone = data.get("phone")
            position = data.get("position", "")
            is_primary = data.get("is_primary")
            

            if not employer_id:
                messages.error(request, "employerIDIsRequired.")
                return JsonResponse({'error': 'employerIDIsRequired.'}, status=400)

            if EmployerContact.objects.filter(email=email).exists():
                messages.error(request, "Email already exists.")
                return JsonResponse({'error': 'emailAlreadyExists.'}, status=400)

            try:
                employer = Organization.objects.get(id=employer_id)
            except Organization.DoesNotExist:
                messages.error(request, "Employer not found.")
                return JsonResponse({'error': 'employerNotFound.'}, status=404)

            EmployerContact.objects.create(
                employer=employer,
                name=name,
                email=email,
                phone=phone,
                position=position,
                is_primary=is_primary
            )

            messages.success(request, _("ContactAssignedSuccessfully!"))
            return JsonResponse({'success': True, 'message': 'ContactAssignedSuccessfully!'})

        except Exception as e:
            messages.error(request, str(e))
            return JsonResponse({'error': str(e)}, status=500)

    def get(self, request, *args, **kwargs):
        messages.error(request, "GET not allowed")
        return JsonResponse({'error': 'GET not allowed.'}, status=405)


@method_decorator(csrf_exempt, name='dispatch')
class AssignEmployersToRecruiterOrgView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            employer_ids = data.get('employer_org_id')
            recruiter_org_id = data.get('recruiter_org_id')

            if not employer_ids or not recruiter_org_id:
                msg = _('missingEmployerIDsorRecruiterOrganizationID.')
                messages.error(request, msg)
                return JsonResponse({'success': False, 'message': msg})

            recruiter_org = get_object_or_404(Organization, id=recruiter_org_id, type='recruiter')
            recruiters = User.objects.filter(organizations=recruiter_org)

            for employer_id in employer_ids:
                employer_org = get_object_or_404(Organization, id=employer_id, type='employer')

                EmployerRecruiterOrgLink.objects.get_or_create(
                    employer_org=employer_org,
                    recruiter_org=recruiter_org
                )

                for recruiter in recruiters:
                    EmployerRecruiter.objects.get_or_create(employer=employer_org, recruiter=recruiter)

                try:
                    primary_contacts = EmployerContact.objects.filter(employer=recruiter_org, is_primary=True)

                    if primary_contacts.exists():
                        for primary_contact in primary_contacts:
                            protocol = 'https' if request.is_secure() else 'http'
                            domain = request.get_host()
                            subject = "Recruiter Assignment Notification"
                            accept_url = f"{protocol}://{domain}/update-employer-recruiter-status/?action=accept&employer_org_id={employer_org.id}&recruiter_org_id={recruiter_org.id}&primary_contact_id={primary_contact.id}"
                            reject_url = f"{protocol}://{domain}/update-employer-recruiter-status/?action=reject&employer_org_id={employer_org.id}&recruiter_org_id={recruiter_org.id}&primary_contact_id={primary_contact.id}"
                            message = f"""
                        Hi {primary_contact.name},

                        Your organization '{employer_org.name}' has been assigned a new recruiter organization: '{recruiter_org.name}'.

                        You can accept or reject the assignment:

                        - Accept: <a href="{accept_url}">Accept</a>
                        - Reject: <a href="{reject_url}">Reject</a>

                        Please click one of the links to confirm your action.

                        Best regards,  
                        Your Team
                        """
                            send_mail(
                                subject,
                                message,
                                'prasanth.s@krify.com',  
                                [primary_contact.email],
                                fail_silently=False
                            )
                except EmployerContact.DoesNotExist:
                    print(f"No primary contact found for employer: {employer_org.name}")

            msg = _('EmployersAssignedSuccessfully.')
            messages.success(request, msg)
            return JsonResponse({'success': True, 'message': msg})

        except json.JSONDecodeError:
            msg = _('invalidJSONData.')
            messages.error(request, msg)
            return JsonResponse({'success': False, 'message': msg})

        except Exception as e:
            messages.error(request, str(e))
            return JsonResponse({'success': False, 'message': str(e)})


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

        # ✅ Block re-use of the link
        if relation.status in ['accepted', 'rejected']:
            return JsonResponse({
                'success': False,
                'message': f'This assignment has already been {relation.status}.'
            })

        if action == 'accept':
            relation.status = 'accepted'
            msg = _('You have accepted the recruiter assignment.')
            subject = "Recruiter Assignment Accepted"
            message = f"Your organization '{employer_org.name}' has successfully accepted the assignment from '{recruiter_org.name}'."

        elif action == 'reject':
            relation.status = 'rejected'
            msg = _('You have rejected the recruiter assignment.')
            subject = "Recruiter Assignment Rejected"
            message = f"Your organization '{employer_org.name}' has rejected the assignment from '{recruiter_org.name}'."

        else:
            return JsonResponse({'success': False, 'message': 'Invalid action.'})

        # Save status and updater
        relation.user_updated_by = primary_contact
        relation.save()

        # Send confirmation email
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
            status__in=['accepted', 'rejected', 'pending']
        ).select_related(
            'employer_org',
            'recruiter_org',
            'user_updated_by__user'  # Optimizes access to user fields in template
        )

class EmployerRecruiterOrgLinkDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        link = get_object_or_404(EmployerRecruiterOrgLink, pk=pk, deleted=False)

        # Optional: Add permission logic here
        if request.user.groups.filter(name='admin').exists():
            link_str = str(link)
            link.delete(user=request.user)
            messages.success(request, _('Link "%(link_str)s" deleted successfully.') % {'link_str': link_str})

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'})

            return redirect('recruiting_web:recruiter-status-list')  # Adjust to your list view name
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'forbidden'}, status=403)

            return HttpResponseForbidden(_("You do not have permission to delete this link."))


class SummaryViews(View):
    def get(self, request, pk, role_id):
        work_assign_form = WorkerAssignmentForm()
        form = FilterWorkExperienceForm()
        filter_form = AdvancedFilterForm()

        search_query = request.GET.get('search', '')
        page_number = request.GET.get('page', 1)
        per_page = request.GET.get('per_page', 25)
        tab = request.GET.get('tab', 'shortlist')

        try:
            per_page = int(per_page)
        except ValueError:
            per_page = 4

        work_request = get_object_or_404(WorkRequests, pk=pk)
        role = get_object_or_404(Role, pk=role_id)
        work_requests = WorkRequests.objects.filter(status='Open').prefetch_related('roles')

        session_key = f'role_{role_id}_state'
        if session_key in request.session:
            state = request.session[session_key]
            search_query = state.get('search_query', '')
            page_number = state.get('page_number', 1)
            per_page = state.get('per_page', 25)

        workers = User.objects.filter(groups__name='worker').distinct().order_by('-created_at')

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

        request.session[session_key] = {
            'search_query': search_query,
            'page_number': page_number,
            'per_page': per_page,
        }

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'workers': worker_data,
                'num_pages': paginator.num_pages
            })
            
        shortlisted_count = len(shortlisted_workers_data)
        offersent_count = len(offersent_workers_data)
        confirmed_count = len(confirmed_workers_data)

        context = {
            'workers': page_obj,
            'work_requests': work_requests,
            'form': form,
            'work_assign_form': work_assign_form,
            'filter_form': filter_form,
            'search_query': search_query,
            'paginator': paginator,
            'per_page': per_page,
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
            messages.success(request, 'EmploymentLocationUpdatedSuccessfully.')
            return redirect('recruiting_web:workrequest_detail', pk=location.role.work_request.pk)
        else:
            messages.error(request, 'ThereWasAnErrorUpdatingTheEmploymentLocation.')


class DeleteEmploymentLocationView(View):
    def post(self, request, pk):
        location = get_object_or_404(EmploymentLocation, pk=pk)
        try:
            location.delete()
            messages.success(request, 'EmploymentLocationDeletedSuccessfully.')
            return redirect('recruiting_web:workrequest_detail', pk=location.role.work_request.pk)
        except Exception as e:
            messages.error(request, f'ErrorDeletingEmploymentLocation: {str(e)}')


class EditHousingInformationView(View):
    def post(self, request, pk):
        housing = get_object_or_404(HousingInformation, pk=pk)
        form = RoleHousingInformationForm(request.POST, instance=housing)
        if form.is_valid():
            form.save()
            messages.success(request, 'HousingInformationUpdatedSuccessfully.')
            return redirect('recruiting_web:workrequest_detail', pk=housing.role.work_request.pk)
        else:
            messages.error(request, 'ThereWasAnErrorUpdatingTheHousingInformation.')
            return redirect('recruiting_web:workrequest_detail', pk=housing.role.work_request.pk)


class DeleteHousingInformationView(View):
    def post(self, request, pk):
        housing = get_object_or_404(HousingInformation, pk=pk)
        try:
            work_request_pk = housing.role.work_request.pk  # Store before deleting
            housing.delete()
            messages.success(request, 'HousingInformationDeletedSuccessfully.')
            return redirect('recruiting_web:workrequest_detail', pk=work_request_pk)
        except Exception as e:
            messages.error(request, f'ErrorDeletingHousingInformation: {str(e)}')
            return redirect('recruiting_web:workrequest_detail', pk=housing.role.work_request.pk)