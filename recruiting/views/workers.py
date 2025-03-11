from django.contrib import messages
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views import View
from django.views.generic import CreateView

from account.models import User, UserWorkExperience
from common.views import BaseCreateView
from recruiting.forms import WorkerCreateForm, WorkExperienceCreateForm
from theme.forms import AdvancedFilterForm, FilterWorkExperienceForm


class WorkerListView(View):
    def get(self, request):
        form = FilterWorkExperienceForm()
        filter_form = AdvancedFilterForm()
        workers = User.objects.filter(groups__name='worker').order_by('-created_at')
        context = {
            'workers': workers,
            'form': form,
            'filter_form': filter_form
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
        context = {'worker': worker}
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
        return render(request, 
            'recruiting/workers/work_experience_detail.html', context)
