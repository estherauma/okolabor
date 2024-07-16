from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import View

from recruiting.forms import EmployerForm, WorkRequestForm
from recruiting.models import Employer, WorkRequests
from django.views.generic import CreateView


class EmployerListView(View):
    def get(self, request):
        employers = Employer.objects.all()
        context = {'employers': employers}
        return render(request, 'recruiting/employers/list.html', context)


class EmployerCreateView(CreateView):
    model = Employer
    form_class = EmployerForm
    template_name = 'recruiting/employers/create.html'

    def form_valid(self, form):
        messages.success(self.request, 'Employer created successfully')
        return super(EmployerCreateView, self).form_valid(form)

    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{field}: {error}')
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse('recruiting_web:employer_detail', kwargs={'pk': self.object.pk})


class EmployerDetailView(View):
    def get(self, request, pk):
        employer = get_object_or_404(Employer, pk=pk)
        context = {'employer': employer}
        print(employer)
        return render(request, 'recruiting/employers/detail.html', context)


class WorkRequestsListView(View):
    def get(self, request):
        work_requests = WorkRequests.objects.all()
        context = {'work_requests': work_requests}
        return render(request, 'recruiting/work_requests/list.html', context)


class WorkRequestCreateView(CreateView):
    model = WorkRequests
    form_class = WorkRequestForm
    template_name = 'recruiting/work_requests/create.html'

    def form_valid(self, form):
        messages.success(self.request, 'Work Request created successfully')
        return super(WorkRequestCreateView, self).form_valid(form)

    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{field}: {error}')
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse('recruiting_web:workrequest_detail', kwargs={'pk': self.object.pk})


class WorkRequestDetailView(View):
    def get(self, request, pk):
        work_request = get_object_or_404(WorkRequests, pk=pk)
        context = {'work_request': work_request}
        return render(request, 'recruiting/work_requests/detail.html', context)
