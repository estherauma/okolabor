from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import View

from recruiting.forms import (
    EmployerForm, RoleDeductionForm,RoleEmploymentLocationForm,
    RoleHoursForm, RoleHousingInformationForm, RoleMealProvision, RoleQualificationForm,
    RoleWagesForm, WorkRequestForm, WorkRequestRoleForm
)
from recruiting.models import Deduction, Employer, EmploymentLocation, Hours, HousingInformation, MealProvision, Qualification, Role, Wages, WorkRequests
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
        return reverse(
            'recruiting_web:employer_detail',
            kwargs={'pk': self.object.pk}
        )


class EmployerDetailView(View):
    def get(self, request, pk):
        employer = get_object_or_404(Employer, pk=pk)
        context = {'employer': employer}
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
        return reverse(
            'recruiting_web:workrequest_detail',
            kwargs={'pk': self.object.pk}
        )


class WorkRequestDetailView(View):
    def get(self, request, pk):
        work_request = get_object_or_404(WorkRequests, pk=pk)
        context = {'workrequest': work_request}
        return render(request, 'recruiting/work_requests/detail.html', context)


class WorkRequestRoleCreateView(CreateView):
    model = Role
    form_class = WorkRequestRoleForm
    template_name = 'recruiting/work_requests/create_role.html'
    
    def get_initial(self):
        initial = super().get_initial()
        initial['work_request'] = self.kwargs.get('pk')

        return initial
    
    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        messages.success(self.request, 'Role created successfully')
        return super().form_valid(form)

    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{field}: {error}')
        return super().form_invalid(form)
    
    def get_success_url(self) -> str:
        return reverse(
            'recruiting_web:workrequest_detail',
            kwargs={'pk': self.object.work_request.pk}
        )


class RoleDataBaseView(CreateView):
    def get_initial(self):
        initial = super().get_initial()
        initial['role'] = self.kwargs.get('pk')
        return initial

    def get_success_url(self) -> str:
        return reverse(
            'recruiting_web:workrequest_detail',
            kwargs={'pk': self.object.role.work_request.pk}
        )

    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{field}: {error}')
        return super().form_invalid(form)

    def form_valid(self, form):
        form.instance.role_id = self.kwargs.get('pk')
        return super().form_valid(form)

class RoleHoursCreateView(RoleDataBaseView):
    model = Hours
    form_class = RoleHoursForm
    template_name = 'recruiting/work_requests/create_hours.html'
    
    def form_valid(self, form):
        messages.success(self.request, 'Role hours successfully added')
        return super().form_valid(form)


class RoleWagesCreateView(RoleDataBaseView):
    model = Wages
    form_class = RoleWagesForm
    template_name = 'recruiting/work_requests/create_wages.html'
    
    def form_valid(self, form):
        messages.success(self.request, 'Roles wages successfully added')
        return super().form_valid(form)


class RoleDeductionsCreateView(RoleDataBaseView):
    model = Deduction
    form_class = RoleDeductionForm
    template_name = 'recruiting/work_requests/create_deductions.html'

    def form_valid(self, form):
        messages.success(self.request, 'Roles deductions successfully added')
        return super().form_valid(form)    
    


class RoleQualificationsCreateView(RoleDataBaseView):
    model = Qualification
    form_class = RoleQualificationForm
    template_name = 'recruiting/work_requests/create_qualifications.html'


class RoleEmpLocationCreateView(RoleDataBaseView):
    model = EmploymentLocation
    form_class = RoleEmploymentLocationForm
    template_name = 'recruiting/work_requests/create_employment_location.html'
    
    def form_valid(self, form):
        messages.success(self.request, 'Successfully added role location')
        return super().form_valid(form)
    

class RoleHousingCreateView(RoleDataBaseView):
    model = HousingInformation
    form_class = RoleHousingInformationForm
    template_name = 'recruiting/work_requests/create_housing_info.html'

    def form_valid(self, form):
        messages.success(self.request, 'Successfully added role housing information')
        return super().form_valid(form)

class RoleMealsCreateView(RoleDataBaseView):
    model = MealProvision
    form_class = RoleMealProvision
    template_name = 'recruiting/work_requests/create_meal_provision.html'
    
    def form_valid(self, form):
        messages.success(self.request, 'Successfully added role meals information')
        return super().form_valid(form)
