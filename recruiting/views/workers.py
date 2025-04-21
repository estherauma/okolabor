from django.contrib import messages
import os
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.models import Group
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views import View
from django.views.generic import CreateView
from django.db.models import Q
from account.models import User, UserWorkExperience, UserJobExperience,UserJobExperienceDetails
from common.views import BaseCreateView
from recruiting.forms import WorkerCreateForm, WorkExperienceCreateForm,WorkerAssignmentForm
from theme.forms import AdvancedFilterForm, FilterWorkExperienceForm,DynamicWorkExperienceForm
from account.models import UserPreference,UserDocuments
from recruiting.models import WorkAssignment,WorkAssignment,WorkRequests,Role
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from content.models import AggregatedContent
from content.serializers import AggregatedContentSerializer
import pandas as pd
from django.http import HttpResponse
import json
from datetime import date
from recruiting.utils import get_sector_choices


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
        page_number = request.GET.get('page', 1)
        per_page = request.GET.get('per_page', 25)

        try:
            per_page = int(per_page)
        except ValueError:
            per_page = 25

        workers = User.objects.filter(groups__name='worker').order_by('-created_at')

        # 🔍 Search Filter
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

        if dynamic_field_1:
            workers = workers.filter(
                crop_experiences__type_details__iexact=dynamic_field_1
            )

        if dynamic_field_2:
            workers = workers.filter(
                crop_experiences__job_experience_details__value__iexact=dynamic_field_2
            )

        # 🔍 Advanced Filter Form (from UserPreference model)
        if filter_form.is_valid():
            for field_name, value in filter_form.cleaned_data.items():
                if value:
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
            profile_completion = self.calculate_profile_completion(worker)
            worker_details = self.get_worker_preferences(worker)

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
                **worker_details
            })

        # 🔄 AJAX Support
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'workers': worker_data,
                'num_pages': paginator.num_pages
            })

        # 🌐 Full Page Render
        context = {
            'workers': page_obj,
            'work_requests': WorkRequests.objects.filter(status='Open').prefetch_related('roles'),
            'form': form,
            'work_assign_form': work_assign_form,
            'filter_form': filter_form,
            'search_query': search_query,
            'paginator': paginator,
            'per_page': per_page,
        }
        return render(request, 'recruiting/workers/list.html', context)

    def calculate_profile_completion(self, user):
        """Calculate the profile completion percentage for a user"""
        user_preferences = UserPreference.objects.filter(user=user, key__in=ONBOARDING_STEPS)
        user_prefs_dict = {pref.key: pref.value.lower() == "true" for pref in user_preferences}
        completed_steps = sum(user_prefs_dict.get(step, False) for step in ONBOARDING_STEPS)
        total_steps = len(ONBOARDING_STEPS)

        return round((completed_steps / total_steps) * 100, 2) if total_steps > 0 else 0

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

    
class AssignWorkerView(View):
    def post(self, request):
        try:
            worker_ids_str = request.POST.get("worker_ids")  
            work_request_id = request.POST.get("work_request") 
            role_id = request.POST.get("role") 
            status = request.POST.get("status", "Assigned")

            if not worker_ids_str or not work_request_id or not role_id:
                messages.error(request, _("missingDataPleaseSelectWorkersWorkRequestAndRole"))
                return JsonResponse({"success": False, "message": "Missing data"}, status=400)

            worker_ids = worker_ids_str.split(",") 
            work_request = get_object_or_404(WorkRequests, id=work_request_id)
            role = get_object_or_404(Role, id=role_id)

            for worker_id in worker_ids:
                worker = get_object_or_404(User, id=worker_id)

                work_assignment, created = WorkAssignment.objects.get_or_create(
                    worker=worker,
                    role=role,
                    defaults={'status': status, 'work_request': work_request}
                )

                if not created:
                    work_assignment.status = status
                    work_assignment.work_request = work_request
                    work_assignment.save()

            messages.success(request, _("workersAssignedSuccessfully!"))
            return redirect("recruiting_web:workers")

        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return JsonResponse({"success": False, "message": str(e)}, status=400)



@method_decorator(csrf_exempt, name='dispatch')
class GetWorkerDetailsView(View):
    def post(self, request, *args, **kwargs):
        worker_ids = request.POST.getlist('worker_ids[]') 
        workers = User.objects.filter(id__in=worker_ids)

        workers_data = [{'id': worker.id, 'firstname': worker.first_name, 'lastname': worker.last_name, 'email': worker.email} for worker in workers]

        return JsonResponse({'workers': workers_data})



class WorkerCreateView(CreateView):
    model = User
    form_class = WorkerCreateForm
    template_name = 'recruiting/workers/create.html'

    def form_valid(self, form):
        worker = form.save()
        try:
            worker_group = Group.objects.get(name='worker')
            worker.groups.add(worker_group)
        except Group.DoesNotExist:
            messages.error(self.request,_("workerGroupDoesNotExist.PleaseCreateIt."))
            return super().form_invalid(form)

        messages.success(self.request, _('workerCreatedSuccessfully.'))
        worker.save()

        return super(WorkerCreateView, self).form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{field}: {error}')
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse(
            'recruiting_web:worker_detail',
            kwargs={'pk': self.object.pk}
        )


class WorkerDetailsView(View):
    def get(self, request, pk):
        worker = get_object_or_404(User, pk=pk)
        base_url = request.build_absolute_uri('/')
        work_experience = UserWorkExperience.objects.filter(user=worker).first()
        preferences = UserPreference.objects.filter(user=worker)

        preference_data = {pref.key: pref.value for pref in preferences}

        workplaces = preference_data.get('workplaces', '').split(',') if 'workplaces' in preference_data else []
        preferred_employees = preference_data.get('Prefered_Employes', '').split(',') if 'Prefered_Employes' in preference_data else []

        documents = UserDocuments.objects.filter(user=worker)
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
        context = {
            'worker': worker,
            'preferences': preference_data,
            'workplaces': workplaces,
            'preferred_employees': preferred_employees,
            'documents': document_dict,
            'base_url': base_url
        }
        return render(request, 'recruiting/workers/detail.html', context)

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
    
    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.cleaned_data['user']
        work_experience = self.object

        # Get selected sector and convert to readable label
        selected_sector = form.cleaned_data.get('type_sector', 'General')
        sector_dict = dict(get_sector_choices())
        print(sector_dict,"sector_dict")
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
            'license': self.request.FILES.get('license_file'),
            'explanation_video': self.request.FILES.get('video_file'),
        }

        for kind, uploaded_file in uploaded_files.items():
            if uploaded_file:
                folder = 'certificates' if kind in ['visa', 'license'] else 'explanation'
                filename = uploaded_file.name
                relative_path = os.path.join('uploads', folder, filename)
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

        messages.success(request, f"Documents uploaded for {user.get_full_name() or user.username}.")
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
            folder = "uploads/english_videos"
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

        messages.success(request, "languageProficiencyInformationSavedSuccessfully.")
        return redirect(reverse("recruiting_web:worker_detail", kwargs={"pk": user.pk}))


class UploadUserPreferenceView(View):
    def post(self, request, *args, **kwargs):
        worker_id = request.POST.get("worker_id")
        user = get_object_or_404(User, id=worker_id)

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

        messages.success(request, "userPreferencesSavedSuccessfully.")
        return redirect(reverse("recruiting_web:worker_detail", kwargs={"pk": user.pk}))

