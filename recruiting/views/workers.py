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
from recruiting.models import WorkAssignment,WorkAssignment,WorkRequests
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

        work_requests = WorkRequests.objects.filter(status='Open')


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

        # Handle AJAX request for worker selection
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            workers_data = [
                {
                    'id': worker.id,
                    'firstname': worker.first_name,
                    'lastname': worker.last_name,
                    'email': worker.email
                }
                for worker in page_obj
            ]
            return JsonResponse({'workers': workers_data, 'num_pages': paginator.num_pages})

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
        status = request.POST.get('status', 'Assigned')

        if not worker_ids or not work_request_ids:
            return JsonResponse({'error': 'Invalid request, missing data'}, status=400)

        work_requests = WorkRequests.objects.filter(id__in=work_request_ids)
        if not work_requests.exists():
            return JsonResponse({'error': 'Invalid work requests'}, status=400)

        for worker_id in worker_ids:
            worker = get_object_or_404(User, id=worker_id)

            # Create or update WorkAssignment for each worker
            work_assignment, created = WorkAssignment.objects.get_or_create(worker=worker)

            # Add multiple work requests to the worker's assignment
            work_assignment.work_request.set(work_requests)  # Use `.set()` for ManyToManyField
            work_assignment.status = status
            work_assignment.save()

        return JsonResponse({'success': 'Workers assigned successfully!'})


    

class AssignWorkerView(View):
    def post(self, request):
        try:
            worker_ids_str = request.POST.get("worker_ids")  # Comma-separated worker IDs
            work_request_ids = request.POST.getlist("work_request")  # Get multiple work request IDs
            status = request.POST.get("status", "Assigned")

            if not worker_ids_str or not work_request_ids:
                messages.error(request, "Missing data. Please select workers and work requests.")
                return JsonResponse({"success": False, "message": "Missing data"}, status=400)

            worker_ids = worker_ids_str.split(",")  # Convert to list
            
            for worker_id in worker_ids:
                worker = get_object_or_404(User, id=worker_id)

                # Create or update a WorkAssignment object for the worker
                work_assignment, created = WorkAssignment.objects.get_or_create(
                    worker=worker,
                    defaults={'status': status}
                )

                # Add multiple work requests to the assignment
                work_requests = WorkRequests.objects.filter(id__in=work_request_ids)
                work_assignment.work_request.set(work_requests)  # Use `.set()` for ManyToManyField

                if not created:
                    work_assignment.status = status
                    work_assignment.save()

            messages.success(request, "Workers assigned successfully!")
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

    
# class WorkerAssignmentCreateView(CreateView):
#     model = WorkAssignment
#     form_class = WorkerAssignmentForm
#     template_name = 'recruiting/worker_assignments/create.html'

#     def form_valid(self, form):
#         messages.success(self.request, _('Worker assigned successfully.'))
#         return super(WorkerAssignmentCreateView, self).form_valid(form)

#     def form_invalid(self, form):
#         for field, errors in form.errors.items():
#             for error in errors:
#                 messages.error(self.request, f'{field}: {error}')
#         return super().form_invalid(form)

#     def get_success_url(self):
#         work_request_id = self.object.work_request.id
#         return reverse('recruiting_web:list_assignments', kwargs={'work_request_id': work_request_id})
    



# @method_decorator(csrf_exempt, name='dispatch')
# class GetWorkerDetailsView(View):
#     def post(self, request, *args, **kwargs):
#         worker_ids = request.POST.getlist('worker_ids')
#         if not worker_ids:
#             return JsonResponse({'error': 'No worker IDs provided'}, status=400)

#         workers = User.objects.filter(id__in=worker_ids).values('id', 'first_name', 'last_name', 'email')
#         worker_list = [{"id": worker["id"], "name": f"{worker['first_name']} {worker['last_name']} ({worker['email']})"} for worker in workers]
#         return JsonResponse({'workers': worker_list})


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
