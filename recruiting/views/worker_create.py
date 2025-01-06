from django.urls import reverse
from account.models import User
from recruiting.forms import WorkerCreateForm
from django.views.generic import CreateView
from django.contrib import messages
from django.contrib.auth.models import Group


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
            messages.error(self.request, "Worker group does not exist. Please create it.")
            return super().form_invalid(form)

        messages.success(self.request, 'Worker created successfully.')
        worker.save()
        
        messages.success(self.request, 'Worker created successfully')
        return super(WorkerCreateView, self).form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{field}: {error}')
        return super().form_invalid(form)
    
    def get_success_url(self):
        # return reverse(
        #     'recruiting_web:worker-detail',
        #     kwargs={'pk': self.object.pk}
        # )
        return reverse('recruiting_web:workers')
