from django.contrib import messages
import os
from django.conf import settings
from django.http import JsonResponse,HttpResponseRedirect,HttpResponseForbidden
from django.contrib.auth.models import Group
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import CreateView,TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from account.models import User, UserWorkExperience, UserJobExperience,UserJobExperienceDetails,UserNotification
from common.views import BaseCreateView
from recruiting.forms import SendMessageForm, WorkerCreateForm, WorkExperienceCreateForm,WorkerAssignmentForm
from theme.forms import AdvancedFilterForm,DynamicWorkExperienceForm
from account.models import UserPreference,UserDocuments
from recruiting.models import WorkAssignment,WorkAssignment,WorkRequests,Role
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from content.models import AggregatedContent
from content.serializers import AggregatedContentSerializer
from django.db import transaction
import pandas as pd
from dateutil.relativedelta import relativedelta
from django.http import HttpResponse
import json
from datetime import date,datetime
from recruiting.utils import calculate_months_ofH2A_expererience, check_visa_status, filter_workers_by_experience, find_worker_status, get_sector_choices
from common.utils import StaticContent
from recruiting.utils import calculate_total_experience,calculate_profile_completion,get_worker_preferences
from common.logger import AppLogger
from django.contrib.auth import get_user_model
from common.firebase_utils import send_push_notification
from django.utils import translation
from django.db.models.functions import Lower
from decimal import Decimal
from django.db.models import Count


ONBOARDING_STEPS = [
    "profileStepOne",
    "workExperienceList",
    "documentsStepOne",
    "levelOfProficiency",
    "recordVideo",
    "workPreferenceStepOne",
    "workPreferenceStepTwo"
]

worker_profile_status_labels = {
    "available": _("workerDetailsAvailable"),
    "on_contract": _("workerDetailsOnContract"),
}

class WorkerListView(LoginRequiredMixin, View):
    def get(self, request):
        # if coming from add workers button on work request detail page
        # Get optional parameters from query string
        role_id = request.GET.get('role')
        work_request_id = request.GET.get('work_request')
        work_assign_form = WorkerAssignmentForm()
        form = DynamicWorkExperienceForm(request.GET or None)
        filter_form = AdvancedFilterForm(request.GET or None)
        search_query = request.GET.get('search', '')

        workers = User.objects.filter(groups__name='worker', deleted=False).order_by('-created_at')
        
       

        # 🔍 Experience Filters
        type_sector = request.GET.get('type_sector')
        dynamic_field_1 = request.GET.getlist('dynamic_field_1')
        dynamic_field_2 = request.GET.getlist('dynamic_field_2')
        params = request.GET
        workers = filter_workers_by_experience(
            workers,
            {
                "type_sector": type_sector,
                "dynamic_field_1": dynamic_field_1,
                "dynamic_field_2": dynamic_field_2,
            },
        )
        
          # Filter workers with duplicate curps
        duplicate_curp_filter = next((v for k, v in params.items() if k.startswith("duplicate_curps") and v), None)
        if duplicate_curp_filter and duplicate_curp_filter.lower() == 'yes':
            duplicate_curp_users = (
                User.objects.filter(groups__name='worker', deleted=False)
                .values('curp')
                .annotate(count=Count('curp'))
                .filter(count__gt=1)
                .values_list('curp', flat=True)
            )
            workers = workers.filter(curp__in=duplicate_curp_users)

        # Filter by Passport
        passport_filter = next((v for k, v in params.items() if k.startswith("passport_") and v), None)
        if passport_filter and passport_filter.lower() == 'yes':
            workers = workers.filter(documents__kind__iexact='passport').distinct()

        # Filter by H2A Experience
        h2a_experience_filter = next((v for k, v in params.items() if k.startswith("h2a_experience_") and v), None)
        if h2a_experience_filter and h2a_experience_filter.lower() == 'yes':
            h2a_user_ids = UserWorkExperience.objects.filter(
                visa_type__iexact="H-2A"
            ).values_list('user_id', flat=True).distinct()

            workers = workers.filter(id__in=h2a_user_ids)

        # Filter by H2B Experience
        h2b_experience_filter = next((v for k, v in params.items() if k.startswith("h2b_experience_") and v), None)
        if h2b_experience_filter and h2b_experience_filter.lower() == 'yes':
            h2b_user_ids = UserWorkExperience.objects.filter(
                visa_type__iexact="H-2B"
            ).values_list('user_id', flat=True).distinct()

            workers = workers.filter(id__in=h2b_user_ids)

        # Filter: Visa
        visa_filter = next((v for k, v in params.items() if k.startswith("visa_") and v), None)
        if visa_filter:
            if visa_filter.lower() == 'yes':
                workers = workers.filter(documents__kind='visa').exclude(documents__path__isnull=True).exclude(documents__path__exact='')
            elif visa_filter.lower() == 'no':
                workers = workers.exclude(documents__kind='visa', documents__path__isnull=False).exclude(documents__kind='visa', documents__path__exact='')

        # Filter: Explanation Video
        video_filter = next((v for k, v in params.items() if k.startswith("explanation_video_") and v), None)
        if video_filter:
            if video_filter.lower() == 'yes':
                workers = workers.filter(documents__kind='explanation_video').exclude(documents__path__isnull=True).exclude(documents__path__exact='')
            elif video_filter.lower() == 'no':
                workers = workers.exclude(documents__kind='explanation_video', documents__path__isnull=False).exclude(documents__kind='explanation_video', documents__path__exact='')

        # Filter by US Driving License
        us_license_filter = next((v for k, v in params.items() if k.startswith("us_driving_license_") and v), None)
        if us_license_filter and us_license_filter.lower() == 'yes':
            workers = workers.filter(documents__kind='us_driving_license')

        # Filter by Mexico/US Driving License
        mx_us_license_filter = next((v for k, v in params.items() if k.startswith("mx_us_driving_license_") and v), None)
        if mx_us_license_filter and mx_us_license_filter.lower() == 'yes':
            workers = workers.filter(
                documents__kind='mexico_driving_license'
            )

        # Filter by Work Preference Type
        work_type_filter = next((v for k, v in params.items() if k.startswith("work_preference_type_") and v), None)
        if work_type_filter:
            work_type_values = [v.strip().lower() for v in work_type_filter.split(',') if v.strip()]
            workers = workers.filter(
                userpreference__key='kindOfWork',
                userpreference__value__in=[val.title() for val in work_type_values]  # Adjust casing as needed
            )

        # Filter by Work Preference Location (multiple comma-separated values)
        work_location_filter = next((v for k, v in params.items() if k.startswith("work_preference_location_") and v), None)
        if work_location_filter:
            location_values = [loc.strip().lower() for loc in work_location_filter.split(',') if loc.strip()]
            workers = workers.filter(
                userpreference__key='whereYouWantToWork',
                userpreference__value__in=[loc.title() for loc in location_values]  # match case (if needed)
            )

        # Filter by English Proficiency if marked 'yes'
        language_proficiency_filter = next((v for k, v in params.items() if k.startswith("language_proficiency_") and v), None)
        if language_proficiency_filter and language_proficiency_filter.lower() == 'yes':
            workers = workers.filter(
                userpreference__key='english_proficiency',
                userpreference__value__iexact='fluent'
            )

        # Filter by Gender
        gender_filter = next((v for k, v in params.items() if k.startswith("gender_") and v), None)
        if gender_filter:
            workers = workers.filter(gender__iexact=gender_filter)

        # Filter by Availability
        availability_from = next((v for k, v in params.items() if k.startswith("availability_from_") and v), None)
        availability_to = next((v for k, v in params.items() if k.startswith("availability_to_") and v), None)
        if availability_from or availability_to:
            availability_filter = Q(userpreference__key='availability')
            if availability_from:
                try:
                    availability_filter &= Q(userpreference__value__gte=availability_from)
                except ValueError:
                    pass

            if availability_to:
                try:
                    availability_filter &= Q(userpreference__value__lte=availability_to)
                except ValueError:
                    pass

            workers = workers.filter(availability_filter)

        # Filter by Reference
        references_filter = next((v for k, v in params.items() if k.startswith("references_") and v), None)
        if references_filter and references_filter.lower() == 'yes':
            referenced_user_ids = UserWorkExperience.objects.filter(
                Q(supervisor_name__isnull=False) & ~Q(supervisor_name__exact='') |
                Q(supervisor_tel__isnull=False) & ~Q(supervisor_tel__exact='') |
                Q(supervisor_email__isnull=False) & ~Q(supervisor_email__exact='')
            ).values_list('user_id', flat=True).distinct()

            workers = workers.filter(id__in=referenced_user_ids)

        # Filter by Physical Labor Limitations
        exclude_physical_limitations = next((v for k, v in params.items() if k.startswith("exclude_physical_limitations_") and v), None)
        if exclude_physical_limitations and exclude_physical_limitations.lower() == 'yes':
            physical_limitation_keys = [
                'healthStatus',
                'sufferedInjury',
                'longerPeriodsOfTime',
                'workEnvironment'
            ]

            preference_kinds = ['work-preferences', 'workPreferences', 'preference']

            yes_q = (
                Q(value__iexact='yes') |
                Q(value__iexact='true') |
                Q(value='1') |
                Q(value__iexact='y')
            )

            workers_with_limitations = (
                UserPreference.objects
                .filter(key__in=physical_limitation_keys, kind__in=preference_kinds)
                .filter(yes_q)
                .values_list('user_id', flat=True)
                .distinct()
            )

            if workers_with_limitations:
                workers = workers.exclude(id__in=workers_with_limitations)

        # Filter by Age (from dob)

        age_min = next((int(v) for k, v in params.items() if k.startswith("age_min_") and v), None)
        age_max = next((int(v) for k, v in params.items() if k.startswith("age_max_") and v), None)
        if age_min is not None or age_max is not None:
            today = date.today()
            min_dob = today - relativedelta(years=age_max) if age_max is not None else None
            max_dob = today - relativedelta(years=age_min) if age_min is not None else None
            dob_filter = Q()
            if min_dob:
                dob_filter &= Q(dob__gte=min_dob)
            if max_dob:
                dob_filter &= Q(dob__lte=max_dob)

            workers = [w for w in workers if (
                (w.dob is not None) and
                (min_dob is None or w.dob >= min_dob) and
                (max_dob is None or w.dob <= max_dob)
            )]

        # Filter by Experience
        min_exp = next((int(v) for k, v in params.items() if k.startswith("years_of_experience_min_") and v), None)
        max_exp = next((int(v) for k, v in params.items() if k.startswith("years_of_experience_max_") and v), None)
        if min_exp is not None or max_exp is not None:
            filtered = []
            for w in workers:
                years = calculate_total_experience(w)
                if ((min_exp is None or years >= min_exp) and
                    (max_exp is None or years <= max_exp)):
                    filtered.append(w)
            workers = filtered

        # Filter by whether user has language proficiency video
        lang_video_filter = next((v for k, v in params.items() if k.startswith("has_language_proficiency_video") and v), None)
        if lang_video_filter:
            lang_video_filter = lang_video_filter.lower().strip()

            if lang_video_filter == 'yes':
                # Workers who HAVE an English proficiency video
                workers = workers.filter(
                    documents__kind='english_video'
                ).exclude(documents__path__isnull=True).exclude(documents__path__exact='')

            elif lang_video_filter == 'no':
                # Workers who do NOT have an English proficiency video
                workers = workers.exclude(
                    documents__kind='english_video',
                    documents__path__isnull=False,
                ).exclude(documents__path__exact='')

        # Deduplicate workers by ID using a dictionary comprehension.
        workers = list({w.id: w for w in workers}.values())
        worker_data = []

        # Initialize years_of_experience to 0 as a default.
        years_of_experience = 0
        exp_filters = {
            'type_sector': type_sector,
            'dynamic_field_1': dynamic_field_1,
            'dynamic_field_2': dynamic_field_2,
        }
        exp_filters_empty = all(not v for v in exp_filters.values())
        for worker in workers:
            profile_completion = calculate_profile_completion(worker)
            worker_details = get_worker_preferences(worker)
            years_of_experience = '-' if exp_filters_empty else calculate_total_experience(worker, exp_filters)
            latest_assignment = WorkAssignment.objects.filter(worker=worker).order_by('-assigned_date').first()

            worker_status_pref = UserPreference.objects.filter(user=worker, key='worker_status').first()
            if worker_status_pref and (worker_status_pref.value or '').strip():
                value = (worker_status_pref.value or '').strip().lower()
                code = 'on_contract' if value in ['on_contract', 'on contract', 'contract'] else 'available'
            else:
                code = 'on_contract' if (latest_assignment and latest_assignment.status == 'confirmed') else 'available'

            worker.latest_status = worker_profile_status_labels[code]
            worker.latest_status_code = code

            visa_uploaded = UserDocuments.objects.filter(
                user=worker, kind='visa'
            ).exclude(path__isnull=True).exclude(path__regex=r'^\s*$').exists()

            intro_video_uploaded = UserDocuments.objects.filter(
                user=worker, kind='explanation_video'
            ).exclude(path__isnull=True).exclude(path__regex=r'^\s*$').exists()

            for key, value in worker_details.items():
                setattr(worker, key, value)

            worker.years_of_experience = years_of_experience
            worker.profile_completion_percentage = profile_completion
            worker.visa_uploaded = visa_uploaded
            worker.intro_video_uploaded = intro_video_uploaded
            worker.total_months_of_h2a_experience = calculate_months_ofH2A_expererience(worker, exp_filters)

            worker_data.append({
                'id': worker.id,
                'first_name': worker.first_name,
                'last_name': worker.last_name,
                'email': worker.email,
                'profile_completion_percentage': profile_completion,
                'years_of_experience': years_of_experience, 
                'visa_uploaded': visa_uploaded,
                'intro_video_uploaded': intro_video_uploaded,
                'total_months_of_h2a_experience': calculate_months_ofH2A_expererience(worker, exp_filters),
                'latest_status': worker_profile_status_labels[code],
                **worker_details
            })

        worker_form = WorkerCreateForm()
        workers_length = len(workers)
        send_message_form = SendMessageForm()
        context = {
            'workers': workers,
            'work_requests': WorkRequests.objects.filter().order_by(Lower('name')).prefetch_related('roles'),
            'form': form,
            'work_assign_form': work_assign_form,
            'filter_form': filter_form,
            'search_query': search_query,
            'years_of_experience': years_of_experience,
            'status_choices': WorkAssignment.STATUS_CHOICES,
            'worker_form': worker_form,
            'workers_count': workers_length,
            'breadcrumbs': [
                        {'name': _('workerListHome'), 'url': reverse('index')},
                        {'name': _('workerListWorkers'), 'url': None},
                    ],
            'selected_work_request':WorkRequests.objects.filter(id=work_request_id).first() if work_request_id else None,
            'selected_role': Role.objects.filter(id=role_id).first() if role_id else None,
            'send_message_form': send_message_form

        }
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            safe_context = {
                'workers': worker_data,
            }
            return JsonResponse(safe_context)
        return render(request, 'recruiting/workers/manage_tabs/tabs.html', context)

    def post(self, request):
        """Handles worker assignment"""
        worker_ids = request.POST.getlist('worker_ids[]') 
        work_request_ids = request.POST.getlist('work_request')  
        role_ids = request.POST.getlist('role') 
        status = request.POST.get('status', 'Assigned')

        if not worker_ids or not work_request_ids or not role_ids:
            return JsonResponse({'error': 'Invalid request, missing data'}, status=400)

        work_requests = WorkRequests.objects.filter(id__in=work_request_ids)
        roles = Role.objects.filter(id__in=role_ids)

        if not work_requests.exists() or not roles.exists():
            return JsonResponse({'error': 'Invalid work requests or roles'}, status=400)

        for worker_id in worker_ids:
            worker = get_object_or_404(User, id=worker_id)

            for role in roles:
                work_assignment, created = WorkAssignment.objects.get_or_create(worker=worker, role=role)
                work_assignment.work_request = role.work_request
                work_assignment.status = status
                work_assignment.save()

        return JsonResponse({'success': 'Workers assigned successfully!'})

class FilteredWorkersAjaxView(View):
    def get(self, request):
        work_request_id = request.GET.get("work_request")
        role_id = request.GET.get("role")
        status = request.GET.get("status")

        if not work_request_id or not role_id:
            return JsonResponse({'error': 'Missing work request or role'}, status=400)

        all_assignments = WorkAssignment.objects.filter(
            work_request_id=work_request_id,
            role_id=role_id,
            deleted=False
        ).select_related('worker', 'role', 'work_request')

        unique_worker_status_counts = {
            'assigned': set(),
            'offersent': set(),
            'confirmed': set(),
            'rejected': set()
        }

        workers = []
        seen_worker_ids = set()

        for assignment in all_assignments:
            current_status = assignment.status
            worker = assignment.worker
            

            if current_status in unique_worker_status_counts and worker:
                unique_worker_status_counts[current_status].add(worker.id)

            if current_status == status and worker and worker.id not in seen_worker_ids:
                seen_worker_ids.add(worker.id)

                profile_completion = "Yes" if calculate_profile_completion(worker) == 100 else "No"
                worker_details = get_worker_preferences(worker)
                experience = calculate_total_experience(worker)
                h2a_exp = calculate_months_ofH2A_expererience(worker)
                has_visa = check_visa_status(worker)

                workers.append({
                    'id': worker.id,
                    'name': f"{worker.first_name} {worker.last_name}" if worker.first_name and worker.last_name else worker.email,
                    'relExp': experience,
                    'h2aExp': h2a_exp,
                    'offer': find_worker_status(worker),
                    'profile': profile_completion,
                    "visa": has_visa
                })

        status_counts = {k: len(v) for k, v in unique_worker_status_counts.items()}

        return JsonResponse({
            'workers': workers,
            'counts': status_counts
        })
class WorkerEditView(LoginRequiredMixin, View):
    def post(self, request, pk):
        user = request.user
        worker = get_object_or_404(User, pk=pk, groups__name='worker')

        if user.groups.filter(name='admin').exists():
            # Update User model fields
            worker.first_name = request.POST.get('first_name')
            worker.last_name = request.POST.get('last_name')
            worker.email = request.POST.get('email')
            worker.save()

            # Update UserPreference fields
            self.update_user_preference(worker, 'town', request.POST.get('town'))
            self.update_user_preference(worker, 'workExperienceList', request.POST.get('work_experience'))
            self.update_user_preference(worker, 'levelOfProficiency', request.POST.get('english_proficiency'))
            self.update_user_preference(worker, 'locationPreference', request.POST.get('location_preference'))

            latest_status = request.POST.get('latest_status')
            if latest_status:
                assignment = WorkAssignment.objects.filter(worker=worker).order_by('-assigned_date').first()
                if assignment:
                    assignment.status = latest_status
                    assignment.save()

            worker_status = request.POST.get('worker_status')
            if worker_status:
                normalized = worker_status.strip().lower()
                if normalized in ['available', 'on_contract', 'on contract', 'contract']:
                    canonical = 'on_contract' if normalized in ['on_contract', 'on contract', 'contract'] else 'available'
                    self.update_user_preference(worker, 'worker_status', canonical)

            messages.success(request, _('workersListWorker "%(worker_name)s" EditedSuccessfully.') % {'worker_name': worker.first_name})
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'})
            return redirect('recruiting_web:workers')

        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'forbidden'}, status=403)
            return HttpResponseForbidden(_("workersListYouDoNotHavePermissionToEditThisWorker"))

    def update_user_preference(self, user, key, value):
        if value:
            UserPreference.objects.update_or_create(
                user=user,
                key=key,
                defaults={'value': value}
            )

import random
import string
from django.utils.crypto import get_random_string

class WorkerDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        user = request.user
        worker = get_object_or_404(User, pk=pk, groups__name='worker')

        if user.groups.filter(name='admin').exists():
            worker_name = f"{worker.first_name} {worker.last_name}"
            # Randomize identifiable fields
            random_suffix = get_random_string(8)
            worker.first_name = "Deleted"
            worker.last_name = f"User{random_suffix}"
            worker.email = f"deleted_{random_suffix}@example.com"
            worker.curp = get_random_string(18, allowed_chars=string.ascii_uppercase + string.digits)
            worker.telelephone = ''.join(random.choices(string.digits, k=10))

            # Save anonymized worker data
            worker.save()

            # Soft delete
            worker.delete(user=user)  # Assuming this does a soft delete

            messages.success(request, _('workersListWorker "%(worker_name)s" DeletedSuccessfully') % {'worker_name': worker_name})

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'})

            return redirect('recruiting_web:workers')

        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'forbidden'}, status=403)
            return HttpResponseForbidden(_("workersListYouDoNotHavePermissionToDeleteThisWorker"))


class AssignWorkerView(View):
    def post(self, request):
        try:
            worker_ids_str = request.POST.get("worker_ids")
            work_request_id = request.POST.get("work_request")
            role_id = request.POST.get("role")
            status = request.POST.get("status", "assigned")

            if not worker_ids_str or not work_request_id or not role_id:
                messages.error(request, _("workersMissingData.PleaseSelectWorkers,JobOrder,AndRole"))
                return JsonResponse({"success": False, "message": "Missing data"}, status=400)

            worker_ids = worker_ids_str.split(",")
            work_request = get_object_or_404(WorkRequests, id=work_request_id)
            role = get_object_or_404(Role, id=role_id)

            already_assigned = []
            newly_assigned = []

            for worker_id in worker_ids:
                worker = get_object_or_404(User, id=worker_id)

                if WorkAssignment.objects.filter(worker=worker, role=role).exists():
                    already_assigned.append(worker.get_full_name() or worker.first_name)
                else:
                    WorkAssignment.objects.create(
                        worker=worker,
                        role=role,
                        work_request=work_request,
                        status=status
                    )
                    newly_assigned.append(worker.get_full_name() or worker.first_name)

            
            msg_parts = []
            if newly_assigned:
                msg_parts.append(_("workersListSuccessfully assigned: ") + ", ".join(newly_assigned))
            if already_assigned:
                msg_parts.append(_("workersListAlready assigned: ") + ", ".join(already_assigned))

            final_msg = " ".join(msg_parts)
            messages.success(request, final_msg)

            return JsonResponse({"success": True, "message": final_msg}, status=200)

        except Exception as e:
            messages.error(request, str(e))
            return JsonResponse({"success": False, "message": str(e)}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class SendOfferView(View):
    def post(self, request, *args, **kwargs):
        try:
            worker_ids_str = request.POST.get("worker_ids")
            work_request_id = request.POST.get("work_request")
            role_id = request.POST.get("role")

            if not worker_ids_str or not work_request_id or not role_id:
                messages.error(request, _("workersMissingData.PleaseSelectWorkers,JobOrder,AndRole"))
                return JsonResponse({"success": False, "message": "Missing data"}, status=400)

            worker_ids = worker_ids_str.split(",")
            work_request = get_object_or_404(WorkRequests, id=work_request_id)
            role = get_object_or_404(Role, id=role_id)

            users_for_notification = []
            newly_offered = []
            already_offered = []

            with transaction.atomic():
                for worker_id in worker_ids:
                    worker = get_object_or_404(User, id=worker_id)

                    work_assignment, created = WorkAssignment.objects.get_or_create(
                        worker=worker,
                        role=role,
                        work_request=work_request,
                        defaults={'status': 'offersent'}
                    )

                    if created or work_assignment.status != 'offersent':
                        work_assignment.status = 'offersent'
                        work_assignment.save()
                        users_for_notification.append(worker)
                        newly_offered.append(worker.get_full_name() or worker.username)
                    else:
                        already_offered.append(worker.get_full_name() or worker.username)

            for user in users_for_notification:
                current_lang = translation.get_language()
                try:
                    translation.activate(user.language)
                    UserNotification.objects.create(
                        user=user,
                        title=_("workRequestAddNotificationTitle"),
                        message=_("workRequestAddNotificationBody")
                    )

                    if user.push_notification_token:
                        send_push_notification(
                            tokens=[user.push_notification_token],
                            title=str(_('workRequestAddNotificationTitle')),
                            body=str(_('workRequestAddNotificationBody')),
                            data={'type': 'job_offer', 'job_id': role_id}
                        )
                finally:
                    translation.activate(current_lang)

            msg_parts = []
            if newly_offered:
                msg_parts.append(_("workersListSuccessfullySentOfferTo: ") + ", ".join(newly_offered))
            if already_offered:
                msg_parts.append(_("workersListOfferAlreadySentTo: ") + ", ".join(already_offered))

            final_msg = " ".join(msg_parts)
            messages.success(request, final_msg)
            return JsonResponse({'success': True, 'message': final_msg})

        except Exception as e:
            messages.error(request, str(e))
            return JsonResponse({"success": False, "message": str(e)}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class GetWorkerDetailsView(View):
    def post(self, request, *args, **kwargs):
        worker_ids = request.POST.getlist('worker_ids[]') 
        workers = User.objects.filter(id__in=worker_ids)
        workers_data = [{'id': worker.id, 'firstname': worker.first_name, 'lastname': worker.last_name, 'email': worker.email} for worker in workers]
        return JsonResponse({'workers': workers_data})


class WorkerCreateView(LoginRequiredMixin, View):
    def post(self, request):
        form = WorkerCreateForm(request.POST)
        if form.is_valid():
            worker = form.save()
            worker.groups.add(Group.objects.get(name='worker'))
            messages.success(request, "Worker created successfully")
            return HttpResponseRedirect(reverse('recruiting_web:worker_detail', kwargs={'pk': worker.pk}))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


class WorkerDetailsView(LoginRequiredMixin,View):
    def get(self, request, pk):
        logger = AppLogger(log_file='logs/debug.log')
        worker = get_object_or_404(User, pk=pk)
        form = WorkExperienceCreateForm(initial={'user': worker})
        base_url = request.build_absolute_uri('/')
        preferences = UserPreference.objects.filter(user=worker)
        preference_data = {pref.key: pref.value for pref in preferences}
        # They should not be displayed to the user
        tracking_keys = [
            'profileStepOne',
            'workExperience',
            'workExperienceList',
            'documentsStepOne',
            'levelOfProficiency',
            'recordVideo',
            'workPreferenceStepOne',
            'workPreferenceStepTwo',
            'englishProficiencyTwo',
            'suitabilityForWork',
            'profile',
            'documents',
            'englishProficiency',
            'workPreferences',
        ]
        
        # remove keys from data sent.
        for key in tracking_keys:
            preference_data.pop(key, None)
        

        documents = UserDocuments.objects.filter(
            user=worker)
        
        document_dict = {}

        for doc in documents:
            kind = doc.kind.lower() if doc.kind else "other"
            if kind not in document_dict:
                document_dict[kind] = []
            document_dict[kind].append({
                "path": doc.path,
                "file_type": doc.file_type,
                "description": doc.description
            })
        experience_forms = {
            experience.id: WorkExperienceCreateForm(instance=experience)
            for 
            experience in worker.work_experiences.all()
        }
        
        static_content = StaticContent()
        document_labels = static_content.get_document_labels()
        preferred_countries_label = static_content.get_label_for_preference_field("whereYouWantToWork")
        preferred_countries_options = static_content.get_options_for_preference_field("whereYouWantToWork")
        work_sectors_label = static_content.get_label_for_preference_field("kindOfWork")
        work_sectors_options = static_content.get_options_for_preference_field("kindOfWork")
        preferences_note_label = static_content.get_label_for_preference_field("tellUsMore")
        availability_label = static_content.get_label_for_preference_field("availability")
        health_status_label = static_content.get_label_for_preference_field_two("healthStatus")
        health_condition_label = static_content.get_label_for_preference_field_two("HealthCondition")
        suffered_injury_label = static_content.get_label_for_preference_field_two("sufferedInjury")
        longer_period_of_time_label = static_content.get_label_for_preference_field_two("longerPeriodsOfTime")
        consent_label = static_content.get_label_for_preference_field_two("consent")
        physical_activities_label = static_content.get_label_for_preference_field_two("physicalActivities")
        work_environment_label = static_content.get_label_for_preference_field_two("workEnvironment")
        language_options = static_content.get_english_proficiency_options()
        language_label = static_content.get_label_for_field("englishProficiency")

        profile_completion = calculate_profile_completion(worker)
        latest_assignment = WorkAssignment.objects.filter(
            worker=worker
        ).order_by('-assigned_date').first()

        worker_status_pref = UserPreference.objects.filter(user=worker, key='worker_status').first()
        if worker_status_pref and (worker_status_pref.value or '').strip():
            value = (worker_status_pref.value or '').strip().lower()
            code = 'on_contract' if value in ['on_contract', 'on contract', 'contract'] else 'available'
        else:
            code = 'on_contract' if (latest_assignment and latest_assignment.status == 'confirmed') else 'available'
        current_status = worker_profile_status_labels[code]

        worker.level_of_language_proficiency = preference_data.get('level')
        worker_messages = UserNotification.objects.filter(user=worker.id, deleted_at__isnull=True).order_by('-created_at')
        # Capitalise status for display
        for msg in worker_messages:
            if hasattr(msg, 'status'):
                msg.status = str(msg.status).capitalize()
        send_message_form = SendMessageForm()

        context = {
            'work_requests': WorkRequests.objects.filter(status='Open').prefetch_related('roles'),
            'worker': worker,
            'preferences': preference_data,
            'profile_completion': profile_completion,
            'current_status': current_status,
            'documents': document_dict,
            'base_url': base_url,
            'document_labels': document_labels,
            'preferred_countries_label': preferred_countries_label,
            'preferred_countries_options': preferred_countries_options,
            'work_sectors_label': work_sectors_label,
            'work_sectors_options': work_sectors_options,
            'preferences_note_label': preferences_note_label,
            'availability_label': availability_label,
            'health_status_label': health_status_label,
            'health_condition_label': health_condition_label,
            'suffered_injury_label': suffered_injury_label,
            'longer_period_of_time_label': longer_period_of_time_label,
            'consent_label': consent_label,
            'physical_activities_label': physical_activities_label,
            'work_environment_label': work_environment_label,
            'language_options': language_options,
            'language_label': language_label,
            'experience_forms': experience_forms,
            'form': form,
            'worker_messages': worker_messages,
            'breadcrumbs': [
                        {'name': _('workerDetailsHome'), 'url': reverse('index')},
                        {'name': _('workerDetailsWorkers'), 'url': reverse('recruiting_web:workers')},
                        {'name': worker.first_name, 'url': None},
                    ],
            'send_message_form': send_message_form,
            'MEDIA_URL': settings.MEDIA_URL
        }
        return render(request, 'recruiting/workers/detail.html', context)

class EditPreferenceView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        worker_id = kwargs.get("worker_id")  # ✅ Gets the user ID from the URL
        key = kwargs.get("key")              # ✅ Gets the preference key from the URL
        user = get_object_or_404(User, id=worker_id)  # ✅ Validates the user exists
        value = request.POST.get("value")             # ✅ Gets the submitted value

        if value:
            UserPreference.objects.update_or_create(
                user=user,
                key=key,
                kind="preference",
                defaults={"value": value},             # ✅ Updates or creates the preference
            )
            messages.success(request, _("workersListUserPreferenceUpdatedSuccessfully"))  # ✅ Feedback

        return redirect(reverse("recruiting_web:worker_detail", kwargs={"pk": user.pk}))  # ✅ Redirect


class DeletePreferenceView(LoginRequiredMixin, View):
    def post(self, request, worker_id, key):
        user = request.user
        target_user = get_object_or_404(User, id=worker_id)

        # Use filter to catch duplicates safely
        preferences = UserPreference.all_objects.filter(
            user=target_user, key=key, kind="preference", deleted=False
        )

        if not preferences.exists():
            messages.error(request, _("workersListPreference with key '%(key)s' not found.") % {'key': key})
            return redirect(reverse("recruiting_web:worker_detail", kwargs={"pk": target_user.pk}))

        if user.groups.filter(name='admin').exists():
            for pref in preferences:
                pref.delete(user=user)
            messages.success(request, _('workersListPreference "%(key)s" deleted successfully.') % {'key': key})

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'})

            return redirect(reverse("recruiting_web:worker_detail", kwargs={"pk": target_user.pk}))
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'forbidden'}, status=403)

            return HttpResponseForbidden(_("workersListNoPermission"))


class GetRolesForWorkRequestView(View):
    def get(self, request, work_request_id):
        get_object_or_404(WorkRequests, id=work_request_id)

        roles = Role.objects.filter(work_request_id=work_request_id)
        roles_data = [{'id': role.id, 'title': role.title} for role in roles]

        return JsonResponse({'roles': roles_data})


class CreateWorkExperienceView(BaseCreateView):
    model = UserWorkExperience
    form_class = WorkExperienceCreateForm
    template_name = 'recruiting/workers/detail.html'
    content_service = StaticContent()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        User = get_user_model()
        worker = get_object_or_404(User, pk=self.kwargs.get('pk'))
        context['worker'] = worker
        context['breadcrumbs'] = [
                {'name': 'Home', 'url': reverse('index')},
                {'name': 'Workers', 'url': reverse('recruiting_web:workers')},
                {'name': 'Worker Details', 'url': reverse('recruiting_web:worker_detail', kwargs={'pk': worker.pk})},
                {'name': 'Create Work Experience', 'url': None},
            ]
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.cleaned_data['user']
        work_experience = self.object
        # Get selected sector and convert to readable label
        selected_sector = form.cleaned_data.get('type_sector', 'General')
        sector_dict = dict(self.content_service.get_sector_choices())
        readable_sector = sector_dict.get(selected_sector, selected_sector)
        type_details = ''
        responsibilities = [] 

        # Map sector-specific multi-select fields to save details, kind/value
        conditional_fields = {
            'animals': {
                'type_details_key': 'animal_types',
                'responsibilities_key': 'responsibilities_types',
            },
            'crop_and_horticulture': {
                'type_details_key': 'crop_types',
                'responsibilities_key': 'crop_job_types',
            },
            'mechanics': {
                'responsibilities_key': 'mechanic_job_types',
            },
            'worker_supervision': {
                'responsibilities_key': 'supervision_jobs_types',
            },
        }
        # Create a UserJobExperience with sector as job_type
        selected_sector_type_keys = conditional_fields.get(selected_sector, {})

        if selected_sector_type_keys:
            type_details_key = selected_sector_type_keys.get('type_details_key', '')
            type_details_list = form.cleaned_data.get(type_details_key, [])
            type_details = ', '.join(type_details_list)
            responsibilities = form.cleaned_data.get(selected_sector_type_keys.get('responsibilities_key', ''), [])
        job_experience = UserJobExperience.objects.create(
            user=user,
            work_experience=work_experience,
            job_type=readable_sector,
            type_details=type_details,
        )

        # Save uploaded files to UserDocuments and link in details
        uploaded_files = {
            'visa': self.request.FILES.get('visa_file'),
            'certificate': self.request.FILES.get('certificate_file'),
            'explanation_video': self.request.FILES.get('video_file'),
        }

        for kind, uploaded_file in uploaded_files.items():
            if uploaded_file:
                folder = 'certificates' if kind in ['visa', 'certificate'] else 'explanation'
                filename = uploaded_file.name
                relative_path = os.path.join(folder, filename)
                full_path = os.path.join(settings.MEDIA_ROOT, relative_path)

                os.makedirs(os.path.dirname(full_path), exist_ok=True)

                with open(full_path, 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)

                # Save in UserDocuments
                doc, created = UserDocuments.objects.get_or_create(
                    user=user,
                    path=relative_path,
                    kind=kind,
                    defaults={
                        'description': f'{kind.title()} for job experience',
                        'file_type': uploaded_file.content_type
                    }
                )

                # Save in JobExperienceDetails
                UserJobExperienceDetails.objects.create(
                    job_experience=job_experience,
                    kind=kind,
                    value=relative_path,
                    is_attachment=True,
                )

        # Save description field
        description = form.cleaned_data.get('description')
        if description:
            UserJobExperienceDetails.objects.create(
                job_experience=job_experience,
                kind='description',
                value=description,
                is_attachment=False,
            )

        if responsibilities:
            UserJobExperienceDetails.objects.create(
                    job_experience=job_experience,
                    kind='responsibilities',
                    value=', '.join(responsibilities),
                    is_attachment=False,
                )                

        return response

    def get_success_url(self):
        return reverse('recruiting_web:worker_detail', kwargs={'pk': self.object.user.pk})


class WorkExperienceDetailsView(LoginRequiredMixin, View):
    def get(self, request, pk):
        base_url = request.build_absolute_uri('/')
        work_experience = get_object_or_404(UserWorkExperience, pk=pk)
        job_experiences = UserJobExperience.objects.filter(work_experience=work_experience)
        job_experience_details = UserJobExperienceDetails.objects.filter(job_experience__in=job_experiences).all().values()
        
        context = {'work_experience': work_experience,
                   'job_experiences': job_experiences,
            'job_experience_details': job_experience_details,
            'base_url': base_url}
        return render(request, 
            'recruiting/workers/work_experience_detail.html', context)
class ExportWorkerDetailsView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        status_param = request.GET.get('status')
        work_request_id = request.GET.get('work_request')
        role_id = request.GET.get('role')

        status_alias_map = {
            'shortlist': 'assigned',
            'assigned': 'assigned',
            'offersent': 'offersent',
            'confirmed': 'confirmed',
            'rejected': 'rejected',
        }

        statuses = []
        if status_param:
            parts = [s.strip().lower() for s in status_param.split(',') if s.strip()]
            for s in parts:
                mapped = status_alias_map.get(s, s)
                if mapped in dict(WorkAssignment.STATUS_CHOICES):
                    statuses.append(mapped)
        use_assignment_filter = bool(work_request_id or role_id or statuses)

        if use_assignment_filter:
            if not statuses:
                statuses = ['assigned', 'offersent', 'confirmed', 'rejected']
            assignments = WorkAssignment.objects.filter(status__in=statuses)
            if work_request_id:
                assignments = assignments.filter(work_request_id=work_request_id)
            if role_id:
                assignments = assignments.filter(role_id=role_id)
            worker_ids = assignments.values_list('worker_id', flat=True).distinct()
            worker_users = User.objects.filter(id__in=worker_ids)
        else:
            worker_users = User.objects.filter(groups__name='worker')

        excluded_keys = set([
            'profileStepOne',
            'documentsStepOne',
            'levelOfProficiency',
            'recordVideo',
            'workPreferenceStepOne',
            'workPreferenceStepTwo',
            'englishProficiencyTwo',
            'profile',
            'documents',
            'workPreferences',
            'workExperience',
            'workExperienceList',
            'suitabilityForWork',
            'englishProficiency',
        ])

        document_kinds = set()
        for user in worker_users:
            try:
                docs = UserDocuments.objects.filter(user=user)
            except Exception:
                docs = []
            for doc in docs:
                kind = getattr(doc, 'kind', None)
                if kind:
                    document_kinds.add(kind)


        latest = AggregatedContent.objects.latest('created_at')
        serializer = AggregatedContentSerializer(latest, many=False)
        aggregated_data = serializer.data
        content = aggregated_data.get('content', {})
        english_content = content.get('en', {})

        work_pref_step_one = english_content.get('workPreferenceStepOne', {})
        work_pref_step_two = english_content.get('workPreferenceStepTwo', {})
        
        step_one_questions = work_pref_step_one.get('form_questions', []) or work_pref_step_one.get('formQuestions', [])
        step_two_questions = work_pref_step_two.get('form_questions', []) or work_pref_step_two.get('formQuestions', [])
        
        work_pref_fields = []
        work_pref_label_map = {}
        
        for question in step_one_questions + step_two_questions:
            key = question.get('key')
            label = question.get('label') or question.get('pageTitle') or key
            if key and key not in excluded_keys:
                work_pref_fields.append(key)
                work_pref_label_map[key] = label
        
        preference_label_map = {}
        form_sections = ['profileStepOne', 'profileStepTwo']
        for section in form_sections:
            section_data = english_content.get(section, {})
            questions = section_data.get('form_questions', []) or section_data.get('formQuestions', [])
            for question in questions:
                key = question.get('key')
                label = question.get('label') or question.get('pageTitle') or key
                if key and key not in excluded_keys:
                    preference_label_map[key] = label
                if key == 'englishProficiency':
                    english_prof_label = question.get('label') or question.get('pageTitle') or 'Level of English Proficiency'
                    preference_label_map['level'] = english_prof_label
        
        preference_label_map.update(work_pref_label_map)
        
        base_fields = [
            'user_id','email', 'curp','language', 'is_verified', 'created_at', 'updated_at',
            'profile_completion', 'years_of_experience', 'months_of_h2a_experience',
            'latest_status',
        ]

        doc_presence_fields = [f'has_doc_{k}' for k in sorted(document_kinds)]

        work_pref_columns = [work_pref_label_map.get(k, k) for k in work_pref_fields]
        
        other_pref_keys = set()
        for user in worker_users:
            try:
                prefs = UserPreference.objects.filter(user=user)
            except Exception:
                prefs = []
            for pref in prefs:
                key = getattr(pref, 'key', None)
                if key and key not in excluded_keys and key not in work_pref_fields:
                    other_pref_keys.add(key)
        
        ordered_other_pref_fields = sorted(other_pref_keys)
        other_pref_columns = [preference_label_map.get(k, k) for k in ordered_other_pref_fields]
        
        columns = base_fields + work_pref_columns + other_pref_columns + doc_presence_fields
        ordered_pref_fields = work_pref_fields + ordered_other_pref_fields

        rows = []
        for user in worker_users:
            row = {col: '' for col in columns}
            row['user_id'] = getattr(user, 'id', '')
            row['email'] = getattr(user, 'email', '')
            row['curp'] = getattr(user, 'curp', '')
            row['first_name'] = getattr(user, 'first_name', '')
            row['last_name'] = getattr(user, 'last_name', '')
            row['date_of_birth'] = getattr(user, 'dob', '')
            row['telephone'] = getattr(user, 'telelephone', '')
            row['gender'] = getattr(user, 'gender', '')
            row['address'] = getattr(user, 'address_line_1', '')
            row['additional_address_information'] = getattr(user, 'address_line_2', '')
            row['town/city'] = getattr(user, 'city', '')
            row['language'] = getattr(user, 'language', '')
            row['is_verified'] = getattr(user, 'is_verified', False)
            row['created_at'] = getattr(user, 'created_at', None)
            row['updated_at'] = getattr(user, 'updated_at', None)

            try:
                row['profile_completion'] = calculate_profile_completion(user)
            except Exception:
                row['profile_completion'] = ''
            try:
                row['years_of_experience'] = calculate_total_experience(user)
            except Exception:
                row['years_of_experience'] = ''
            try:
                row['months_of_h2a_experience'] = calculate_months_ofH2A_expererience(user)
            except Exception:
                row['months_of_h2a_experience'] = ''

            code = 'available'
            try:
                prefs_for_status = UserPreference.objects.filter(user=user)
            except Exception:
                prefs_for_status = []
            for p in prefs_for_status:
                if getattr(p, 'key', '') == 'worker_status':
                    val = (getattr(p, 'value', '') or '').strip().lower()
                    if val in ['on_contract', 'on contract', 'contract']:
                        code = 'on_contract'
                    else:
                        code = 'available'
                    break
            if code == 'available':
                try:
                    latest_assignment = WorkAssignment.objects.filter(worker=user).order_by('-assigned_date').first()
                    if latest_assignment and getattr(latest_assignment, 'status', '') == 'confirmed':
                        code = 'on_contract'
                except Exception:
                    pass
                
            row['latest_status'] = worker_profile_status_labels.get(code, code)

            pref_map = {}
            try:
                prefs = UserPreference.objects.filter(user=user)
            except Exception:
                prefs = []
            for pref in prefs:
                key = getattr(pref, 'key', None)
                if key and key in ordered_pref_fields:
                    pref_map[key] = getattr(pref, 'value', '')
            for k in ordered_pref_fields:
                label = preference_label_map.get(k, k)
                row[label] = pref_map.get(k, '')


            try:
                user_doc_kinds = set(
                    d.kind for d in UserDocuments.objects.filter(user=user) if getattr(d, 'kind', None)
                )
            except Exception:
                user_doc_kinds = set()
            for k in document_kinds:
                row[f'has_doc_{k}'] = 'Yes' if k in user_doc_kinds else 'No'

            rows.append(row)
            
        rows_cleaned = []
        for row in rows:
            clean_row = {}
            for k, v in row.items():
                if isinstance(v, datetime):
                    v = v.replace(tzinfo=None)
                elif isinstance(v, Decimal):
                    v = float(v)
                elif isinstance(v, bool):
                    v = str(v)
                elif not isinstance(v, (str, int, float, datetime)):
                    v = str(v) if v is not None else ''
                clean_row[k] = v
            rows_cleaned.append(clean_row)


        capitalized_columns = [col.replace('_', ' ').upper() for col in columns]
        df_workers = pd.DataFrame(rows_cleaned, columns=columns)
        df_workers.columns = capitalized_columns
        
        experience_rows = []
        for user in worker_users:
            experiences = UserWorkExperience.objects.filter(user=user)
            if not experiences.exists():
                continue
            worker_row = df_workers[df_workers['USER ID'] == user.id]
            if worker_row.empty:
                continue
            base_data = worker_row.iloc[0].to_dict()
            for exp in experiences:
                exp_row = base_data.copy()
                exp_row.update({
                    'EXPERIENCE ID': getattr(exp, 'id', ''),
                    'JOB TITLE': getattr(exp, 'work_title', ''),
                    'CURRENTLY WORKING': 'Yes' if getattr(exp, 'currently_working', False) else 'No',
                    'COMPANY YOU WORKED FOR': getattr(exp, 'company', ''),
                    'LOCATION': getattr(exp, 'country', ''),
                    'VISA TYPE': getattr(exp, 'visa_type', ''),
                    'SUPERVISOR NAME': getattr(exp, 'supervisor_name', ''),
                    'SUPERVISOR TELEPHONE': getattr(exp, 'supervisor_tel', ''),
                    'SUPERVISOR EMAIL': getattr(exp, 'supervisor_email', ''),
                    'WORK UNDER H2A IN USA': getattr(exp, 'work_under_h2a_in_usa', ''), 
                    'TYPE OF WORK': getattr(exp, 'type_of_work', ''),
                    'APPROXIMATE MONTH AND YEAR YOU STARTED': getattr(exp, 'approx_month_and_year', ''),
                    'APPROXIMATE TOTAL NUMBER OF MONTHS WORKED': getattr(exp, 'approx_total_months_worked', ''),
                })
                
                excluded_detail_kinds = {'job_experience_media', 'explanation_video', 'license', 'evidence', 'visa', 'description', 'responsibilities'}
                job_experiences = UserJobExperience.objects.filter(work_experience=exp)
                job_details_map = {}
                for job_exp in job_experiences:
                    details = UserJobExperienceDetails.objects.filter(job_experience=job_exp)
                    for detail in details:
                        kind = getattr(detail, 'kind', '')
                        value = getattr(detail, 'value', '')
                        if kind and kind not in excluded_detail_kinds:
                            key = f'JOB DETAILS - {kind.upper()}'
                            if key not in job_details_map:
                                job_details_map[key] = []
                            job_details_map[key].append(value)
                
                for key, values in job_details_map.items():
                    exp_row[key] = '; '.join(values)
                
                experience_rows.append(exp_row)
                
        df_experiences = pd.DataFrame(experience_rows)
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="workers.xlsx"'

        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df_workers.to_excel(writer, index=False, sheet_name='Workers')
            if not df_experiences.empty:
                df_experiences.to_excel(writer, index=False, sheet_name='Worker Experiences')

        return response


class UploadDocumentsView(LoginRequiredMixin, View):
    upload_paths = {
    'contract': 'uploads/visa',
    'passport': 'uploads/passports',
    'profile_picture': 'uploads/profiles',
    'english_video': 'uploads/english_videos',
    'us_driving_license': 'uploads/driver_licenses',
    'mexico_driving_license': 'uploads/driver_licenses',
    'certificate': 'uploads/certificates',
    'visa': 'uploads/visa',
    'photo': 'uploads/photos',
    'job_experience_license': 'uploads/job_experiences/licenses',
    'job_experience_media': 'uploads/job_experiences/media',
    'explanation_video': 'uploads/explanation_videos',
    }

    def post(self, request, *args, **kwargs):
        worker_id = request.POST.get("worker_id")
        user = get_object_or_404(User, pk=worker_id)
        for field_name, upload_dir in self.upload_paths.items():
            uploaded_file = request.FILES.get(field_name)
            if uploaded_file:
                filename = uploaded_file.name
                clean_dir = upload_dir.replace('uploads', '').strip('/')
                relative_path = os.path.join(clean_dir, filename)
                full_path = os.path.join(settings.MEDIA_ROOT, relative_path)

                os.makedirs(os.path.dirname(full_path), exist_ok=True)

                try:
                    with open(full_path, 'wb+') as destination:
                        for chunk in uploaded_file.chunks():
                            destination.write(chunk)

                    new_doc = UserDocuments.objects.create(
                        user=user,
                        path=f"uploads/{relative_path}",
                        kind=field_name,
                        description=f'{field_name.replace("_", " ").title()} for user profile',
                        file_type=uploaded_file.content_type
                    )
                    
                    old_docs = UserDocuments.objects.filter(user=user, kind=field_name).exclude(id=new_doc.id)
                    if field_name == 'profile_picture':
                        for old_doc in old_docs:
                            old_file_path = os.path.join(settings.MEDIA_ROOT, old_doc.path)
                            if os.path.exists(old_file_path):
                                try:
                                    os.remove(old_file_path)
                                except Exception:
                                    pass
                        old_docs.delete()

                except Exception as e:
                    messages.error(request, f"Failed to upload {field_name}: {str(e)}")


        text = _('documentsUploadedFor')
        messages.success(request, f"{text} {user.get_full_name() or user.email}.")
        return redirect(reverse('recruiting_web:worker_detail', kwargs={'pk': user.pk}))

class UploadLanguageProficiencyView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        worker_id = request.POST.get("worker_id")
        language_level = request.POST.get("language_level")
        language_video = request.FILES.get("language_video")
        capitalised_level = language_level.capitalize()

        if not worker_id or not language_level:
            messages.error(request, "WorkerOrLanguageLevelIsMissing.")
            return redirect("/")

        user = get_object_or_404(User, id=worker_id)

        UserPreference.objects.update_or_create(
            user=user,
            key="level",
            kind="language",
            defaults={"value": capitalised_level},
        )

        if language_level != "none" and language_video:
            folder = "uploads/explanation"
            filename = language_video.name
            relative_path = os.path.join(folder, filename)
            full_path = os.path.join(settings.MEDIA_ROOT, relative_path)

            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            with open(full_path, "wb+") as destination:
                for chunk in language_video.chunks():
                    destination.write(chunk)

            UserDocuments.objects.create(
                user=user,
                path=relative_path,
                kind="english_video",
                description="English Language Proficiency Video",
                file_type=language_video.content_type,
            )

        messages.success(request, _("languageProficiencyInformationSavedSuccessfully."))
        return redirect(reverse("recruiting_web:worker_detail", kwargs={"pk": user.pk}))


class UploadUserPreferenceView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        worker_id = request.POST.get("worker_id")
        user = get_object_or_404(User, id=worker_id)
        static_content = StaticContent()

        preferences = {
        "whereYouWantToWork": request.POST.getlist("preferred_countries"),
        "kindOfWork": request.POST.getlist("work_sectors"),
        "tellUsMore": request.POST.get("preferences_note"),
        "availability": request.POST.getlist("availability_months"),
        "healthStatus": request.POST.get("healthStatus"),
        "healthCondition": request.POST.get("healthCondition"),
        "suffred_injury": request.POST.get("suffred_injury"),
        "longerPeriodOfTime": request.POST.get("longerPeriodOfTime"),
        "consent": request.POST.get("consent"),
        "physicalActivities": request.POST.get("physicalActivities"),
        "workEnvironment": request.POST.get("workEnvironment"),
        }


        for key, value in preferences.items():
            if value:
                if isinstance(value, list):
                    value = ", ".join(value)

                UserPreference.objects.update_or_create(
                    user=user,
                    key=key,
                    kind="preference",
                    defaults={"value": value},
                )

        messages.success(request, _("userPreferencesSavedSuccessfully."))
        return redirect(reverse("recruiting_web:worker_detail", kwargs={"pk": user.pk}))


class EditWorkExperienceView(LoginRequiredMixin, View):
    def post(self, request, pk):
        work_experience = get_object_or_404(UserWorkExperience, pk=pk)
        form = WorkExperienceCreateForm(request.POST, request.FILES, instance=work_experience)

        if form.is_valid():
            user = form.cleaned_data['user']

            try:
                job_experience = UserJobExperience.objects.filter(work_experience=work_experience).first()
            except UserJobExperience.DoesNotExist:
                messages.error(request, "relatedJobExperienceNotFound.")
                return redirect(reverse('recruiting_web:worker_detail', kwargs={'pk': user.pk}))

            selected_sector = form.cleaned_data.get('type_sector', 'General')
            sector_dict = dict(StaticContent().get_sector_choices())
            readable_sector = sector_dict.get(selected_sector, selected_sector)

            if job_experience.job_type != readable_sector:
                job_experience.job_type = readable_sector
                job_experience.save()

            form.save()

            uploaded_files = {
                'visa': request.FILES.get('visa_file'),
                'certificate': request.FILES.get('certificate_file'),
                'explanation_video': request.FILES.get('video_file'),
            }

            for kind, uploaded_file in uploaded_files.items():
                if uploaded_file:
                    old_doc = UserDocuments.objects.filter(user=user, kind=kind).first()
                    if old_doc:
                        old_path = os.path.join(settings.MEDIA_ROOT, old_doc.path)
                        if os.path.exists(old_path):
                            os.remove(old_path)
                        old_doc.delete()

                    folder = 'certificates' if kind in ['visa', 'certificate'] else 'explanation'
                    filename = uploaded_file.name
                    relative_path = os.path.join('uploads', folder, filename)
                    full_path = os.path.join(settings.MEDIA_ROOT, relative_path)
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)

                    with open(full_path, 'wb+') as destination:
                        for chunk in uploaded_file.chunks():
                            destination.write(chunk)

                    doc = UserDocuments.objects.create(
                        user=user,
                        path=relative_path,
                        kind=kind,
                        description=f'{kind.title()} for job experience',
                        file_type=uploaded_file.content_type
                    )

                    UserJobExperienceDetails.objects.update_or_create(
                        job_experience=job_experience,
                        kind=kind,
                        defaults={'value': relative_path}
                    )

            description = form.cleaned_data.get('description')
            if description:
                UserJobExperienceDetails.objects.update_or_create(
                    job_experience=job_experience,
                    kind='description',
                    defaults={'value': description, 'is_attachment': False}
                )

            conditional_fields = {
                'animals': {
                    'animal_types': 'animal_type',
                    'animal_jobs': 'animal_task',
                },
                'crop_horticulture': {
                    'crop_types': 'crop_type',
                    'crop_jobs': 'crop_task',
                },
                'mechanics': {
                    'mechanic_jobs': 'mechanic_task',
                },
                'worker_supervision': {
                    'supervision_jobs': 'supervision_task',
                },
            }

            fields_for_sector = conditional_fields.get(selected_sector, {})
            for form_field, detail_kind in fields_for_sector.items():
                values = form.cleaned_data.get(form_field)
                if values:
                    UserJobExperienceDetails.objects.filter(
                        job_experience=job_experience,
                        kind=detail_kind,
                    ).delete()

                    for val in values:
                        UserJobExperienceDetails.objects.create(
                            job_experience=job_experience,
                            kind=detail_kind,
                            value=val,
                            is_attachment=False,
                        )

            messages.success(request, 'WorkExperienceUpdatedSuccessfully.')
            return redirect(reverse('recruiting_web:worker_detail', kwargs={'pk': user.pk}))

        messages.error(request, 'ThereWereSomeErrorsInTheForm.')
        return redirect(reverse('recruiting_web:worker_detail', kwargs={'pk': work_experience.user.pk}))

class DeleteWorkExperienceView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        work_experience_id = kwargs.get('pk')
        work_experience = get_object_or_404(UserWorkExperience, pk=work_experience_id,deleted=False)
        user = work_experience.user

        job_experiences = UserJobExperience.objects.filter(work_experience=work_experience,deleted=False)

        for job in job_experiences:
            UserJobExperienceDetails.objects.filter(job_experience=job).delete()

            doc_details = UserJobExperienceDetails.objects.filter(job_experience=job, is_attachment=True)
            for detail in doc_details:
                try:
                    doc = UserDocuments.objects.get(user=user, path=detail.value)
                    doc.delete()
                except UserDocuments.DoesNotExist:
                    pass

            job.delete()

        work_experience.delete(user=request.user)

        messages.success(request, "workExperienceDeletedSuccessfully.")
        return redirect(reverse('recruiting_web:worker_detail', kwargs={'pk': user.pk}))

class EditUserPreferenceView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        worker_id = kwargs.get("worker_id")
        user = get_object_or_404(User, id=worker_id)
        static_content = StaticContent()

        preferences = {}
        fields = {
            "preferred_countries": "whereYouWantToWork",
            "work_sectors": "kindOfWork",
            "preferences_note": "tellUsMore",
            "availability_months": "availability",
            "healthStatus": "healthStatus",
            "healthCondition": "healthCondition",
            "suffred_injury": "suffred_injury",
            "longerPeriodOfTime": "longerPeriodOfTime",
            "consent": "consent",
            "physicalActivities": "physicalActivities",
            "workEnvironment": "workEnvironment",
        }

        for field_name, label in fields.items():
            preference = UserPreference.objects.filter(user=user, key=label, kind="preference").first()
            if preference:
                # split list values
                preferences[field_name] = preference.value.split(", ") if "," in preference.value else preference.value

        return render(request, "your_template.html", {
            "preferences": preferences,
            "worker_id": worker_id,
            # add other context like preferred_countries_options, etc.
        })

    def post(self, request, *args, **kwargs):
        worker_id = kwargs.get("worker_id")
        user = get_object_or_404(User, id=worker_id)
        static_content = StaticContent()

        fields = {
            "preferred_countries": "whereYouWantToWork",
            "work_sectors": "kindOfWork",
            "preferences_note": "tellUsMore",
            "availability_months": "availability",
            "healthStatus": "healthStatus",
            "healthCondition": "healthCondition",
            "suffred_injury": "suffred_injury",
            "longerPeriodOfTime": "longerPeriodOfTime",
            "consent": "consent",
            "physicalActivities": "physicalActivities",
            "workEnvironment": "workEnvironment",
        }

        for field_name, key in fields.items():
            raw_value = request.POST.getlist(field_name) if field_name in ["preferred_countries", "work_sectors", "availability_months"] else request.POST.get(field_name)
            if raw_value:
                value = ", ".join(raw_value) if isinstance(raw_value, list) else raw_value
                obj, created = UserPreference.objects.get_or_create(user=user, key=key, kind="preference", defaults={"value": value})
                if not created and obj.value != value:
                    obj.value = value
                    obj.save()

        messages.success(request, _("workersListUserPreferencesUpdatedSuccessfully"))
        return redirect(reverse("recruiting_web:worker_detail", kwargs={"pk": user.pk}))


class EditLanguageProficiencyView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        worker_id = kwargs.get("worker_id") or request.POST.get("worker_id")
        language_level = request.POST.get("language_level")
        language_video = request.FILES.get("language_video")
        capitalised_level = language_level.strip().capitalize()

        if not worker_id or not language_level:
            messages.error(request, "WorkerOrLanguageLevelIsMissing.")
            return redirect("/")

        user = get_object_or_404(User, id=worker_id)

        # Update or create language level preference
        UserPreference.objects.update_or_create(
            user=user,
            key="level",
            kind="language",
            defaults={"value": capitalised_level},
        )

        # Save video only if selected and uploaded
        if language_level != "none" and language_video:
            folder = "uploads/english_videos"
            filename = language_video.name
            relative_path = os.path.join(folder, filename)
            full_path = os.path.join(settings.MEDIA_ROOT, relative_path)

            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            with open(full_path, "wb+") as destination:
                for chunk in language_video.chunks():
                    destination.write(chunk)

            # Optionally, you might want to delete old videos here

            UserDocuments.objects.create(
                user=user,
                path=relative_path,
                kind="english_video",
                description="English Language Proficiency Video",
                file_type=language_video.content_type,
            )

        messages.success(request, _("languageProficiencyInformationSavedSuccessfully."))
        return redirect(reverse("recruiting_web:worker_detail", kwargs={"pk": user.pk}))


class EditDocumentsView(LoginRequiredMixin, View):
    upload_paths = {
        'passport': 'uploads/passports',
        'profile_picture': 'uploads/profiles',
        'us_driver_license': 'uploads/driver_licenses',
        'mexico_driver_license': 'uploads/driver_licenses',
    }

    def post(self, request, *args, **kwargs):
        worker_id = kwargs.get("worker_id") or request.POST.get("worker_id")
        user = get_object_or_404(User, pk=worker_id)

        for field_name, upload_dir in self.upload_paths.items():
            uploaded_file = request.FILES.get(field_name)
            if not uploaded_file:
                continue

            filename = uploaded_file.name
            clean_dir = upload_dir.replace('uploads', '').strip('/')
            relative_path = os.path.join(clean_dir, filename)
            full_path = os.path.join(settings.MEDIA_ROOT, relative_path)

            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            try:
                with open(full_path, 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)

                new_doc = UserDocuments.objects.create(
                    user=user,
                    path=f"uploads/{relative_path}",
                    kind=field_name,
                    description=f'{field_name.replace("_", " ").title()} for user profile',
                    file_type=uploaded_file.content_type
                )
                
                old_docs = UserDocuments.objects.filter(user=user, kind=field_name).exclude(id=new_doc.id)
                if field_name == 'profile_picture':
                    for old_doc in old_docs:
                        old_file_path = os.path.join(settings.MEDIA_ROOT, old_doc.path)
                    if os.path.exists(old_file_path):
                        try:
                            os.remove(old_file_path)
                        except Exception:
                            pass
                old_docs.delete()
                    
            except Exception as e:
                messages.error(request, f"Failed to upload {field_name}: {str(e)}")
                continue

        messages.success(request, _("workersListDocumentsUpdatedSuccessfully"))
        return redirect(reverse('recruiting_web:worker_detail', kwargs={'pk': user.pk}))


class DeleteAllWorkerInfoView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        worker_id = kwargs.get("worker_id")
        user = get_object_or_404(User, pk=worker_id)
        UserPreference.objects.filter(user=user).delete()
        UserDocuments.objects.filter(user=user).delete()

        messages.success(request, _("workersListAllInformationDeleted"))
        return redirect(reverse('recruiting_web:worker_detail', kwargs={'pk': user.pk}))
