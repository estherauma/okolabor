from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.models import Group
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views import View
from django.views.generic import CreateView
from django.db.models import Q
from account.models import User, UserWorkExperience
from common.views import BaseCreateView
from recruiting.forms import WorkerCreateForm, WorkExperienceCreateForm
from theme.forms import AdvancedFilterForm, FilterWorkExperienceForm
from account.models import UserPreference


class WorkerListView(View):
    def get(self, request):
        form = FilterWorkExperienceForm()
        filter_form = AdvancedFilterForm()
        search_query = request.GET.get('search')
        page_number = request.GET.get('page', 1)

        if search_query:
            workers = User.objects.filter(
                Q(groups__name='worker') &
                (Q(first_name__icontains=search_query) | Q(last_name__icontains=search_query)) | Q(email__icontains=search_query)
            ).order_by('-created_at')
        else:
            workers = User.objects.filter(groups__name='worker').order_by('-created_at')

        paginator = Paginator(workers,4)  # Show 10 workers per page
        page_obj = paginator.get_page(page_number)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Return JSON response for AJAX requests
            workers_data = [{'id': worker.id, 'firstname': worker.first_name, 'lastname': worker.last_name, 'email': worker.email} for worker in page_obj]
            return JsonResponse({'workers': workers_data, 'num_pages': paginator.num_pages})

        context = {
            'workers': page_obj,
            'form': form,
            'filter_form': filter_form,
            'search_query': search_query,
            'paginator': paginator
        }
        return render(request, 'recruiting/workers/list.html', context)

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
            messages.error(self.request,_("Worker group does not exist. Please create it."))
            return super().form_invalid(form)

        messages.success(self.request, _('Worker created successfully.'))
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
        preferences = UserPreference.objects.filter(user=worker)

        # Convert preferences into a dictionary for easy template access
        preference_data = {pref.key: pref.value for pref in preferences}

        workplaces = []
        if 'workplaces' in preference_data:
            workplaces = preference_data['workplaces'].split(',')
        preference_data['workplaces'] = workplaces

        Prefered_Employes = []
        if 'Prefered_Employes' in preference_data:
            Prefered_Employes = preference_data['Prefered_Employes'].split(',')
        preference_data['Prefered_Employes'] = Prefered_Employes

        print(Prefered_Employes,"Prefered_Employes")
        context = {
            'worker': worker,
            'preferences': preference_data,  # Now we have a dictionary for easy access
            'Prefered_Employes': Prefered_Employes,
            'workplaces': workplaces
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
        context = {'work_experience': work_experience}
        print(context,"context")
        return render(request, 
            'recruiting/workers/work_experience_detail.html', context)
