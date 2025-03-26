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
            per_page = 4  # Fallback default

        work_requests = WorkRequests.objects.filter(status='Open').prefetch_related('roles')

        workers = User.objects.filter(groups__name='worker').order_by('-created_at')
        # Filtering workers
        if search_query:
            workers = workers.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query)
            )
        else:
            workers = User.objects.filter(groups__name='worker').order_by('-created_at')

        paginator = Paginator(workers, per_page)
        page_obj = paginator.get_page(page_number)

        # 🔹 Add work experience & preferences to each worker in `page_obj`
        for worker in page_obj:
            # Fetch work experience
            worker.work_experience = list(UserWorkExperience.objects.filter(user=worker).values(
                'work_title', 'company', 'start_date', 'end_date', 'currently_working'
            ))
            worker.profile_completion_percentage = worker.calculate_profile_completion()

            # Fetch user preferences
            preferences = UserPreference.objects.filter(user=worker)
            preference_data = {pref.key: pref.value for pref in preferences}

            # Get "English Proficiency" value or default to "-"
            worker.english_proficiency = preference_data.get("English Proficiency", "-")

        # ✅ If AJAX request, return JSON
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            workers_data = [{
                'id': worker.id,
                'firstname': worker.first_name,
                'lastname': worker.last_name,
                'email': worker.email,
                'city': worker.city,
                'work_experience': worker.work_experience,
                'english_proficiency': worker.english_proficiency,  # Include proficiency
                'profile_completion': worker.profile_completion_percentage
            } for worker in page_obj]
            return JsonResponse({'workers': workers_data, 'num_pages': paginator.num_pages})

        # ✅ Pass updated `page_obj` with `work_experience` and `english_proficiency` to template
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

    def post(self, request):
        """Handles worker assignment"""
        worker_ids = request.POST.getlist('worker_ids[]')  # List of selected workers
        work_request_ids = request.POST.getlist('work_request')  # List of selected work requests
        role_ids = request.POST.getlist('role')  # List of selected roles
        status = request.POST.get('status', 'Assigned')

        if not worker_ids or not work_request_ids or not role_ids:
            return JsonResponse({'error': 'Invalid request, missing data'}, status=400)

        work_requests = WorkRequests.objects.filter(id__in=work_request_ids)
        roles = Role.objects.filter(id__in=role_ids)

        if not work_requests.exists() or not roles.exists():
            return JsonResponse({'error': 'Invalid work requests or roles'}, status=400)

        for worker_id in worker_ids:
            worker = get_object_or_404(User, id=worker_id)

            # Create or update WorkAssignment for each worker
            for role in roles:
                work_assignment, created = WorkAssignment.objects.get_or_create(worker=worker, role=role)
                work_assignment.work_request = role.work_request
                work_assignment.status = status
                work_assignment.save()

        return JsonResponse({'success': 'Workers assigned successfully!'})

    
class AssignWorkerView(View):
    def post(self, request):
        try:
            worker_ids_str = request.POST.get("worker_ids")  # Comma-separated worker IDs
            work_request_id = request.POST.get("work_request")  # Single work request ID
            role_id = request.POST.get("role")  # Single role ID
            status = request.POST.get("status", "Assigned")

            if not worker_ids_str or not work_request_id or not role_id:
                messages.error(request, _("missingDataPleaseSelectWorkersWorkRequestAndRole"))
                return JsonResponse({"success": False, "message": "Missing data"}, status=400)

            worker_ids = worker_ids_str.split(",")  # Convert to list
            work_request = get_object_or_404(WorkRequests, id=work_request_id)
            role = get_object_or_404(Role, id=role_id)

            for worker_id in worker_ids:
                worker = get_object_or_404(User, id=worker_id)

                # Create or update a WorkAssignment object for the worker
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
        worker_ids = request.POST.getlist('worker_ids[]')  # Get selected worker IDs
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

        # Convert preferences into a dictionary

        preference_data = {pref.key: pref.value for pref in preferences}

        # Process specific preferences
        workplaces = preference_data.get('workplaces', '').split(',') if 'workplaces' in preference_data else []
        preferred_employees = preference_data.get('Prefered_Employes', '').split(',') if 'Prefered_Employes' in preference_data else []

        # Fetch user documents categorized by `kind`
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
            'documents': document_dict  # Pass categorized documents
        }
        return render(request, 'recruiting/workers/detail.html', context)

class GetRolesForWorkRequestView(View):
    def get(self, request, work_request_id):
        # Ensure the work request exists
        get_object_or_404(WorkRequests, id=work_request_id)

        # Fetch roles associated with the work request
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
