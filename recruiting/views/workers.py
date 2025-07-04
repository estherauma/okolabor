from django.contrib import messages
import os
from django.conf import settings
from django.http import JsonResponse,HttpResponseRedirect,HttpResponseForbidden
from django.contrib.auth.models import Group
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views import View
from django.views.generic import CreateView,TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from account.models import User, UserWorkExperience, UserJobExperience,UserJobExperienceDetails
from common.views import BaseCreateView
from recruiting.forms import WorkerCreateForm, WorkExperienceCreateForm,WorkerAssignmentForm
from theme.forms import AdvancedFilterForm,DynamicWorkExperienceForm
from account.models import UserPreference,UserDocuments
from recruiting.models import WorkAssignment,WorkAssignment,WorkRequests,Role
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from content.models import AggregatedContent
from content.serializers import AggregatedContentSerializer
import pandas as pd
from dateutil.relativedelta import relativedelta
from django.http import HttpResponse
import json
from datetime import date
from recruiting.utils import get_sector_choices
from common.utils import StaticContent
from recruiting.utils import calculate_total_experience,calculate_profile_completion
from common.logger import AppLogger




ONBOARDING_STEPS = [
    "profileStepOne",
    "workExperienceList",
    "documentsStepOne",
    "levelOfProficiency",
    "recordVideo",
    "workPreferenceStepOne",
    "workPreferenceStepTwo"
]
class WorkerListView(View):
    def get(self, request):
        work_assign_form = WorkerAssignmentForm()
        form = DynamicWorkExperienceForm(request.GET or None)
        filter_form = AdvancedFilterForm(request.GET or None)
        search_query = request.GET.get('search', '')

        workers = User.objects.filter(groups__name='worker').order_by('-created_at')

        # 🔍 Experience Filters
        type_sector = request.GET.get('type_sector')
        dynamic_field_1 = request.GET.get('dynamic_field_1')
        dynamic_field_2 = request.GET.get('dynamic_field_2')
        params = request.GET
        if type_sector:
            workers = workers.filter(
                crop_experiences__job_type__iexact=type_sector
            )

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
        workers = workers.distinct()

        worker_data = []
        for worker in workers:
            profile_completion = self.calculate_profile_completion(worker)
            worker_details = self.get_worker_preferences(worker)
            years_of_experience = calculate_total_experience(worker)
            worker.profile_completion_percentage = profile_completion

            latest_assignment = WorkAssignment.objects.filter(worker=worker).order_by('-assigned_date').first()
            worker.latest_status = latest_assignment.status if latest_assignment else None

            for key, value in worker_details.items():
                setattr(worker, key, value)

            worker_data.append({
                'id': worker.id,
                'firstname': worker.first_name,
                'lastname': worker.last_name,
                'email': worker.email,
                'profile_completion': profile_completion,
                'years_of_experience': years_of_experience, 
                **worker_details
            })
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'workers': worker_data,
                'num_pages': 1  # or len(worker_data) if needed
            })
       
        worker_form = WorkerCreateForm()
        
        shortlisted_assignments = WorkAssignment.objects.filter(
            status='assigned'
        ).select_related('worker', 'role', 'work_request')

        shortlisted_workers = []
        seen_worker_ids = set()
        for assignment in shortlisted_assignments:
            worker = assignment.worker
            if worker and worker.id not in seen_worker_ids:
                seen_worker_ids.add(worker.id)
                shortlisted_workers.append(worker)

        shortlisted_worker_data = []

        for worker in shortlisted_workers:
            profile_completion = self.calculate_profile_completion(worker)
            worker_details = self.get_worker_preferences(worker)
            years_of_experience = calculate_total_experience(worker)
            worker.profile_completion_percentage = profile_completion

            latest_assignment = WorkAssignment.objects.filter(
                worker=worker
            ).select_related('role', 'work_request').order_by('-assigned_date').first()

            status = latest_assignment.status if latest_assignment else None
            work_request_name = (
                latest_assignment.work_request.name
                if latest_assignment and latest_assignment.work_request else None
            )
            role_name = (
                latest_assignment.role.title
                if latest_assignment and latest_assignment.role else None
            )

            for key, value in worker_details.items():
                setattr(worker, key, value)

            shortlisted_worker_data.append({
                'id': worker.id,
                'firstname': worker.first_name,
                'lastname': worker.last_name,
                'email': worker.email,
                'profile_completion': profile_completion,
                'years_of_experience': years_of_experience,
                'work_request': work_request_name,
                'role': role_name,
                'status': status,
                **worker_details
            })

            
        offersent_assignments = WorkAssignment.objects.filter(
            status='offersent'
        ).select_related('worker', 'role', 'work_request')

        offersent_workers = []
        seen_worker_ids = set()
        for assignment in offersent_assignments:
            worker = assignment.worker
            if (
                worker and
                worker.id not in seen_worker_ids and
                not worker.email.startswith("deleted_")
            ):
                seen_worker_ids.add(worker.id)
                offersent_workers.append(worker)

        offersent_worker_data = []
        for worker in offersent_workers:
            profile_completion = self.calculate_profile_completion(worker)
            worker_details = self.get_worker_preferences(worker)
            years_of_experience = calculate_total_experience(worker)
            worker.profile_completion_percentage = profile_completion

            latest_assignment = WorkAssignment.objects.filter(
                worker=worker
            ).select_related('role', 'work_request').order_by('-assigned_date').first()

            status = latest_assignment.status if latest_assignment else None
            work_request_name = (
                latest_assignment.work_request.name
                if latest_assignment and latest_assignment.work_request else None
            )
            role_name = (
                latest_assignment.role.title
                if latest_assignment and latest_assignment.role else None
            )

            offersent_worker_data.append({
                'id': worker.id,
                'firstname': worker.first_name,
                'lastname': worker.last_name,
                'email': worker.email,
                'profile_completion': profile_completion,
                'years_of_experience': years_of_experience,
                'work_request': work_request_name,
                'role': role_name,
                'status': status,
                **worker_details
            })

            
        confirmed_assignments = WorkAssignment.objects.filter(
            status='confirmed'
        ).select_related('worker', 'role', 'work_request')

        confirmed_workers = []
        seen_worker_ids = set()
        for assignment in confirmed_assignments:
            worker = assignment.worker
            if worker and worker.id not in seen_worker_ids:
                seen_worker_ids.add(worker.id)
                confirmed_workers.append(worker)

        confirmed_worker_data = []

        for worker in confirmed_workers:
            profile_completion = self.calculate_profile_completion(worker)
            worker_details = self.get_worker_preferences(worker)
            years_of_experience = calculate_total_experience(worker)
            worker.profile_completion_percentage = profile_completion

            latest_assignment = WorkAssignment.objects.filter(
                worker=worker
            ).select_related('role', 'work_request').order_by('-assigned_date').first()

            work_request_name = (
                latest_assignment.work_request.name
                if latest_assignment and latest_assignment.work_request else None
            )
            role_name = (
                latest_assignment.role.title
                if latest_assignment and latest_assignment.role else None
            )
            status = latest_assignment.status if latest_assignment else None

            worker.latest_status = status

            for key, value in worker_details.items():
                setattr(worker, key, value)

            confirmed_worker_data.append({
                'id': worker.id,
                'firstname': worker.first_name,
                'lastname': worker.last_name,
                'email': worker.email,
                'profile_completion': profile_completion,
                'years_of_experience': years_of_experience,
                'work_request': work_request_name,
                'role': role_name,
                'status': status,
                **worker_details
            })

            
        rejected_assignments = WorkAssignment.objects.filter(
            status='rejected'
        ).select_related('worker', 'role', 'work_request')

        rejected_workers = []
        seen_worker_ids = set()
        for assignment in rejected_assignments:
            worker = assignment.worker
            if worker and worker.id not in seen_worker_ids:
                seen_worker_ids.add(worker.id)
                rejected_workers.append(worker)

        rejected_worker_data = []

        for worker in rejected_workers:
            profile_completion = self.calculate_profile_completion(worker)
            worker_details = self.get_worker_preferences(worker)
            years_of_experience = calculate_total_experience(worker)
            worker.profile_completion_percentage = profile_completion

            latest_assignment = WorkAssignment.objects.filter(
                worker=worker
            ).select_related('role', 'work_request').order_by('-assigned_date').first()

            status = latest_assignment.status if latest_assignment else None
            work_request_name = (
                latest_assignment.work_request.name
                if latest_assignment and latest_assignment.work_request else None
            )
            role_name = (
                latest_assignment.role.title
                if latest_assignment and latest_assignment.role else None
            )

            worker.latest_status = status

            for key, value in worker_details.items():
                setattr(worker, key, value)

            rejected_worker_data.append({
                'id': worker.id,
                'firstname': worker.first_name,
                'lastname': worker.last_name,
                'email': worker.email,
                'profile_completion': profile_completion,
                'years_of_experience': years_of_experience,
                'work_request': work_request_name,
                'role': role_name,
                'status': status,
                **worker_details
            })

        workers_length = len(workers)
        shortlisted_workers_length = len(shortlisted_workers)
        offersent_workers_length = len(offersent_workers)
        confirmed_workers_length = len(confirmed_workers)
        rejected_workers_length = len(rejected_workers)
        

        context = {
            'workers': workers,
            'shortlisted_workers':shortlisted_worker_data,
            'offersent_workers':offersent_worker_data,
            'confirmed_workers':confirmed_worker_data,
            'rejected_workers':rejected_worker_data,
            'work_requests': WorkRequests.objects.filter(status='Open').prefetch_related('roles'),
            'form': form,
            'work_assign_form': work_assign_form,
            'filter_form': filter_form,
            'search_query': search_query,
            'years_of_experience': years_of_experience,
            'status_choices': WorkAssignment.STATUS_CHOICES,
            'worker_form': worker_form,
            'workers_count': workers_length,
            'shortlisted_count': shortlisted_workers_length,
            'offersent_count': offersent_workers_length,
            'confirmed_count': confirmed_workers_length,
            'rejected_count': rejected_workers_length,
        }
        return render(request, 'recruiting/workers/manage_tabs/tabs.html', context)

    def calculate_profile_completion(self, user):
        """Calculate the profile completion percentage for a user"""
        user_preferences = UserPreference.objects.filter(user=user, key__in=ONBOARDING_STEPS)
        user_prefs_dict = {pref.key: pref.value.lower() == "true" for pref in user_preferences}
        completed_steps = sum(user_prefs_dict.get(step, False) for step in ONBOARDING_STEPS)
        total_steps = len(ONBOARDING_STEPS)

        return round((completed_steps / total_steps) * 100) if total_steps > 0 else 0

    def get_worker_preferences(self, user):
        """Fetch town, work experience, proficiency, and location preference from UserPreference"""
        preference_keys = ["town", "workExperienceList", "levelOfProficiency", "locationPreference"]

        preferences = UserPreference.objects.filter(user=user, key__in=preference_keys).values("key", "value")
    
        worker_details = {pref["key"]: pref["value"] for pref in preferences}

        return {
            "town": worker_details.get("town", "Not Provided"),
            "work_experience": worker_details.get("workExperienceList", "Not Provided"),
            "english_proficiency": worker_details.get("levelOfProficiency", "Not Provided"),
            "location_preference": worker_details.get("locationPreference", "Not Provided"),
        }

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
    

    def get_worker_preferences(self, user):
        keys = ["town", "workExperienceList", "levelOfProficiency", "locationPreference"]
        preferences = UserPreference.objects.filter(user=user, key__in=keys).values("key", "value")
        pref_dict = {pref["key"]: pref["value"] for pref in preferences}

        return {
            "town": pref_dict.get("town", "Not Provided"),
            "work_experience": pref_dict.get("workExperienceList", "Not Provided"),
            "english_proficiency": pref_dict.get("levelOfProficiency", "Not Provided"),
            "location_preference": pref_dict.get("locationPreference", "Not Provided"),
        }

    
        
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

            # Optionally, update status (from WorkAssignment)
            latest_status = request.POST.get('latest_status')
            if latest_status:
                assignment = WorkAssignment.objects.filter(worker=worker).order_by('-assigned_date').first()
                if assignment:
                    assignment.status = latest_status
                    assignment.save()

            messages.success(request, _('Worker "%(worker_name)s" EditedSuccessfully.') % {'worker_name': worker.first_name})
            
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'})
            return redirect('recruiting_web:workers')

        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'forbidden'}, status=403)
            return HttpResponseForbidden(_("YouDoNotHavePermissionToEditThisWorker."))

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
            worker_name = f"{worker.first_name} {worker.last_name}"
            worker.delete(user=user)  # Assuming this does a soft delete

            messages.success(request, _('Worker "%(worker_name)s" DeletedSuccessfully.') % {'worker_name': worker_name})

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'})

            return redirect('recruiting_web:workers')

        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'forbidden'}, status=403)
            return HttpResponseForbidden(_("youDoNotHavePermissionToDeleteThisWorker."))

    
class AssignWorkerView(View):
    def post(self, request):
        try:
            worker_ids_str = request.POST.get("worker_ids")
            work_request_id = request.POST.get("work_request")
            role_id = request.POST.get("role")
            status = request.POST.get("status", "Assigned")

            if not worker_ids_str or not work_request_id or not role_id:
                messages.error(request, _("Missing data. Please select workers, work request, and role."))
                return JsonResponse({"success": False, "message": _("Missing data.")}, status=400)

            worker_ids = worker_ids_str.split(",")
            work_request = get_object_or_404(WorkRequests, id=work_request_id)
            role = get_object_or_404(Role, id=role_id)

            already_assigned = []
            newly_assigned = []

            for worker_id in worker_ids:
                worker = get_object_or_404(User, id=worker_id)

                if WorkAssignment.objects.filter(worker=worker, role=role).exists():
                    already_assigned.append(worker.get_full_name() or worker.username)
                else:
                    WorkAssignment.objects.create(
                        worker=worker,
                        role=role,
                        work_request=work_request,
                        status=status
                    )
                    newly_assigned.append(worker.get_full_name() or worker.username)

            
            msg_parts = []
            if newly_assigned:
                msg_parts.append(_("Successfully assigned: ") + ", ".join(newly_assigned))
            if already_assigned:
                msg_parts.append(_("Already assigned: ") + ", ".join(already_assigned))

            final_msg = " ".join(msg_parts)
            messages.success(request, final_msg)

            return JsonResponse({"success": True, "message": final_msg}, status=200)

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



class WorkerCreateView(View):
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


class WorkerDetailsView(View):
    def get(self, request, pk):
        logger = AppLogger(log_file='logs/debug.log')
        worker = get_object_or_404(User, pk=pk)
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

        current_status = latest_assignment.status if latest_assignment else 'No Assignment'
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
            'experience_forms': experience_forms
        }
        return render(request, 'recruiting/workers/detail.html', context)
    
class EditPreferenceView(View):
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
            messages.success(request, _("User preference updated successfully."))  # ✅ Feedback

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
            messages.error(request, _("Preference with key '%(key)s' not found.") % {'key': key})
            return redirect(reverse("recruiting_web:worker_detail", kwargs={"pk": target_user.pk}))

        if user.groups.filter(name='admin').exists():
            for pref in preferences:
                pref.delete(user=user)
            messages.success(request, _('Preference "%(key)s" deleted successfully.') % {'key': key})

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'})

            return redirect(reverse("recruiting_web:worker_detail", kwargs={"pk": target_user.pk}))
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'forbidden'}, status=403)

            return HttpResponseForbidden(_("You do not have permission to delete this preference."))


class GetRolesForWorkRequestView(View):
    def get(self, request, work_request_id):
        get_object_or_404(WorkRequests, id=work_request_id)

        roles = Role.objects.filter(work_request_id=work_request_id)
        roles_data = [{'id': role.id, 'title': role.title} for role in roles]

        return JsonResponse({'roles': roles_data})
    

class CreateWorkExperienceView(BaseCreateView):
    model = UserWorkExperience
    form_class = WorkExperienceCreateForm
    template_name = 'recruiting/workers/work_experience_create.html'
    content_service = StaticContent()
    
    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.cleaned_data['user']
        work_experience = self.object
        # Get selected sector and convert to readable label
        selected_sector = form.cleaned_data.get('type_sector', 'General')
        sector_dict = dict(self.content_service.get_sector_choices())
        readable_sector = sector_dict.get(selected_sector, selected_sector)

        # Create a UserJobExperience with sector as job_type
        job_experience = UserJobExperience.objects.create(
            user=user,
            work_experience=work_experience,
            job_type=readable_sector
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

        # Map sector-specific multi-select fields to be saved as kind/value
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

        # Save each selected option from relevant fields to details
        fields_for_sector = conditional_fields.get(selected_sector, {})
        for form_field, detail_kind in fields_for_sector.items():
            values = form.cleaned_data.get(form_field)
            if values:
                for val in values:
                    UserJobExperienceDetails.objects.create(
                        job_experience=job_experience,
                        kind=detail_kind,
                        value=val,
                        is_attachment=False,
                    )

        return response

    def get_success_url(self):
        return reverse('recruiting_web:worker_detail', kwargs={'pk': self.object.user.pk})



class WorkExperienceDetailsView(View):
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



class ExportWorkerDetailsView(View):
    def get(self, request, *args, **kwargs):
        latest = AggregatedContent.objects.latest('created_at')
        serializer = AggregatedContentSerializer(latest, many=False)
        aggregated_data = serializer.data
        content = aggregated_data.get('content', {})
        english_content = content.get('en', {})

        work_preference_step_one = english_content.get('workPreferenceStepOne', {}).get('form_questions', [])
        work_preference_step_two = english_content.get('workPreferenceStepTwo', {}).get('form_questions', [])
        profile_step_one = english_content.get('profileStepOne', {}).get('form_questions', [])
        profile_step_two = english_content.get('profileStepTwo', {}).get('form_questions', [])

        profile_step_two_questions = profile_step_two
        profile_step_two_page_title = english_content.get('profileStepTwo', {}).get('pageTitle', "")

        english_proficiency_title = next(
            (q.get("label") for q in profile_step_two_questions if q.get("key") == "englishProficiency"),
            profile_step_two_page_title
        ) or "What is your level of English proficiency?"

        excluded_keys = {
            "English Proficiency",
            "profileStepOne",
            "profile",
            "workExperienceList",
            "workExperience",
            "documentsStepOne",
            "documents",
            "levelOfProficiency",
            "englishProficiency",
            "workPreferenceStepTwo",
            "workPreferences",
            "suitabilityForWork",
            "workPreferenceStepOne",
            "recordVideo",
            "englishProficiencyTwo",
        }

        filtered_questions = [
            q for q in (work_preference_step_one + work_preference_step_two + profile_step_one + profile_step_two)
            if q['key'] not in excluded_keys
        ]

        preference_label_map = {q['key']: q.get('label', q['key']) for q in filtered_questions}

        if "englishProficiency" in preference_label_map:
            preference_label_map["englishProficiency"] = english_proficiency_title

        data = []
        worker_users = User.objects.filter(groups__name="worker")

        for user in worker_users:
            preferences = UserPreference.objects.filter(user=user)
            worker_data = {}

            for pref in preferences:
                if pref.key not in excluded_keys:
                    question_label = preference_label_map.get(pref.key, pref.key)
                    worker_data[question_label] = pref.value

            if worker_data:
                data.append(worker_data)

        df = pd.DataFrame(data)

        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response["Content-Disposition"] = 'attachment; filename="worker_preferences.xlsx"'

        with pd.ExcelWriter(response, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Worker Preferences")

        return response
    

class UploadDocumentsView(View):
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
                relative_path = os.path.join(upload_dir, filename)
                full_path = os.path.join(settings.MEDIA_ROOT, relative_path)

                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)
                UserDocuments.objects.create(
                    user=user,
                    path=relative_path,
                    kind=field_name,
                    description=f'{field_name.replace("_", " ").title()} for user profile',
                    file_type=uploaded_file.content_type
                )

        text = _('documentsUploadedFor')
        messages.success(request, f"{text} {user.get_full_name() or user.email}.")
        return redirect(reverse('recruiting_web:worker_detail', kwargs={'pk': user.pk}))
    
class UploadLanguageProficiencyView(View):
    def post(self, request, *args, **kwargs):
        worker_id = request.POST.get("worker_id")
        language_level = request.POST.get("language_level")
        language_video = request.FILES.get("language_video")

        if not worker_id or not language_level:
            messages.error(request, "WorkerOrLanguageLevelIsMissing.")
            return redirect("/")

        user = get_object_or_404(User, id=worker_id)

        UserPreference.objects.update_or_create(
            user=user,
            key="english_proficiency",
            kind="language",
            defaults={"value": language_level},
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


class UploadUserPreferenceView(View):
    def post(self, request, *args, **kwargs):
        worker_id = request.POST.get("worker_id")
        user = get_object_or_404(User, id=worker_id)
        static_content = StaticContent()

        preferences = {
        static_content.get_label_for_preference_field("whereYouWantToWork"): request.POST.getlist("preferred_countries"),
        static_content.get_label_for_preference_field("kindOfWork"): request.POST.getlist("work_sectors"),
        static_content.get_label_for_preference_field("tellUsMore"): request.POST.get("preferences_note"),
        static_content.get_label_for_preference_field("availability"): request.POST.getlist("availability_months"),
        static_content.get_label_for_preference_field_two("healthStatus"): request.POST.get("healthStatus"),
        static_content.get_label_for_preference_field_two("healthCondition"): request.POST.get("healthCondition"),
        static_content.get_label_for_preference_field_two("suffred_injury"): request.POST.get("suffred_injury"),
        static_content.get_label_for_preference_field_two("longerPeriodOfTime"): request.POST.get("longerPeriodOfTime"),
        static_content.get_label_for_preference_field_two("consent"): request.POST.get("consent"),
        static_content.get_label_for_preference_field_two("physicalActivities"): request.POST.get("physicalActivities"),
        static_content.get_label_for_preference_field_two("workEnvironment"): request.POST.get("workEnvironment"),
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
    


class EditWorkExperienceView(View):
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

class DeleteWorkExperienceView(View):
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
    
class EditUserPreferenceView(View):
    def get(self, request, *args, **kwargs):
        worker_id = kwargs.get("worker_id")
        user = get_object_or_404(User, id=worker_id)
        static_content = StaticContent()

        preferences = {}
        fields = {
            "preferred_countries": static_content.get_label_for_preference_field("whereYouWantToWork"),
            "work_sectors": static_content.get_label_for_preference_field("kindOfWork"),
            "preferences_note": static_content.get_label_for_preference_field("tellUsMore"),
            "availability_months": static_content.get_label_for_preference_field("availability"),
            "healthStatus": static_content.get_label_for_preference_field_two("healthStatus"),
            "healthCondition": static_content.get_label_for_preference_field_two("healthCondition"),
            "suffred_injury": static_content.get_label_for_preference_field_two("suffred_injury"),
            "longerPeriodOfTime": static_content.get_label_for_preference_field_two("longerPeriodOfTime"),
            "consent": static_content.get_label_for_preference_field_two("consent"),
            "physicalActivities": static_content.get_label_for_preference_field_two("physicalActivities"),
            "workEnvironment": static_content.get_label_for_preference_field_two("workEnvironment"),
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
            "preferred_countries": static_content.get_label_for_preference_field("whereYouWantToWork"),
            "work_sectors": static_content.get_label_for_preference_field("kindOfWork"),
            "preferences_note": static_content.get_label_for_preference_field("tellUsMore"),
            "availability_months": static_content.get_label_for_preference_field("availability"),
            "healthStatus": static_content.get_label_for_preference_field_two("healthStatus"),
            "healthCondition": static_content.get_label_for_preference_field_two("healthCondition"),
            "suffred_injury": static_content.get_label_for_preference_field_two("suffred_injury"),
            "longerPeriodOfTime": static_content.get_label_for_preference_field_two("longerPeriodOfTime"),
            "consent": static_content.get_label_for_preference_field_two("consent"),
            "physicalActivities": static_content.get_label_for_preference_field_two("physicalActivities"),
            "workEnvironment": static_content.get_label_for_preference_field_two("workEnvironment"),
        }

        for field_name, key in fields.items():
            raw_value = request.POST.getlist(field_name) if field_name in ["preferred_countries", "work_sectors", "availability_months"] else request.POST.get(field_name)
            if raw_value:
                value = ", ".join(raw_value) if isinstance(raw_value, list) else raw_value
                obj, created = UserPreference.objects.get_or_create(user=user, key=key, kind="preference", defaults={"value": value})
                if not created and obj.value != value:
                    obj.value = value
                    obj.save()

        messages.success(request, _("userPreferencesUpdatedSuccessfully."))
        return redirect(reverse("recruiting_web:worker_detail", kwargs={"pk": user.pk}))


class EditLanguageProficiencyView(View):
    def post(self, request, *args, **kwargs):
        worker_id = kwargs.get("worker_id") or request.POST.get("worker_id")
        language_level = request.POST.get("language_level")
        language_video = request.FILES.get("language_video")

        if not worker_id or not language_level:
            messages.error(request, "WorkerOrLanguageLevelIsMissing.")
            return redirect("/")

        user = get_object_or_404(User, id=worker_id)

        # Update or create language level preference
        UserPreference.objects.update_or_create(
            user=user,
            key="english_proficiency",
            kind="language",
            defaults={"value": language_level},
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
    

class EditDocumentsView(View):
    upload_paths = {
        'passport': 'uploads/passports',
        'profile_picture': 'uploads/profiles',
        'us_driving_license': 'uploads/driver_licenses',
        'mexico_driving_license': 'uploads/driver_licenses',
    }

    def post(self, request, *args, **kwargs):
        worker_id = kwargs.get("worker_id") or request.POST.get("worker_id")
        user = get_object_or_404(User, pk=worker_id)

        for field_name, upload_dir in self.upload_paths.items():
            uploaded_file = request.FILES.get(field_name)
            if uploaded_file:
                filename = uploaded_file.name
                relative_path = os.path.join(upload_dir, filename)
                full_path = os.path.join(settings.MEDIA_ROOT, relative_path)

                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)

                # Delete old file of the same kind if it exists
                UserDocuments.objects.filter(user=user, kind=field_name).delete()

                UserDocuments.objects.create(
                    user=user,
                    path=relative_path,
                    kind=field_name,
                    description=f'{field_name.replace("_", " ").title()} for user profile',
                    file_type=uploaded_file.content_type
                )

        messages.success(request, _("Documents updated successfully."))
        return redirect(reverse('recruiting_web:worker_detail', kwargs={'pk': user.pk}))


class DeleteAllWorkerInfoView(View):
    def post(self, request, *args, **kwargs):
        worker_id = kwargs.get("worker_id")
        user = get_object_or_404(User, pk=worker_id)
        UserPreference.objects.filter(user=user).delete()
        UserDocuments.objects.filter(user=user).delete()

        messages.success(request, _("All information related to the worker has been deleted."))
        return redirect(reverse('recruiting_web:worker_detail', kwargs={'pk': user.pk}))


