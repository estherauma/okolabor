from django.contrib import messages
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
from theme.forms import AdvancedFilterForm, FilterWorkExperienceForm
from account.models import UserPreference,UserDocuments
from recruiting.models import WorkAssignment,WorkAssignment,WorkRequests,Role
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json

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
        form = FilterWorkExperienceForm()
        filter_form = AdvancedFilterForm()
        search_query = request.GET.get('search', '')
        page_number = request.GET.get('page', 1)
        per_page = request.GET.get('per_page', 25)

        try:
            per_page = int(per_page)
        except ValueError:
            per_page = 4  

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
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'workers': worker_data,
                'num_pages': paginator.num_pages
            })

        context = {
            'workers': page_obj,
            'work_requests': work_requests,
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
        # Set the user as a worker
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
            'documents': document_dict  
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
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'recruiting_web:worker_detail',
            kwargs={'pk': self.object.user.pk}
        )


class WorkExperienceDetailsView(View):
    def get(self, request, pk):
        work_experience = get_object_or_404(UserWorkExperience, pk=pk)
        job_experiences = UserJobExperience.objects.filter(work_experience=work_experience)
        job_experience_details = UserJobExperienceDetails.objects.filter(job_experience__in=job_experiences)
        context = {'work_experience': work_experience,
                   'job_experiences': job_experiences,
            'job_experience_details': job_experience_details}
        return render(request, 
            'recruiting/workers/work_experience_detail.html', context)
