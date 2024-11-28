from django.shortcuts import render
from django.views import View
from account.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
# from account.forms.account_update import UpdateAccountDetailsForm
from account.forms import UserLogsFilterForm

class UserListView(LoginRequiredMixin, View):
    def get(self, request):
        users = User.objects.filter(groups__name='recruiter')
        pending = User.objects.filter(
            is_active=False,
            groups__name='recruiter')
        context = {'users': users, 'pending_users': pending}
        return render(request, 'recruiter/manage_users.html', context)


class UserActivitLogView(LoginRequiredMixin, View):
    def get(self, request):
        
        form = UserLogsFilterForm()
        user = User.objects.get(pk=request.user.id)
        logs = user.audit_logs.all()
        context = {'logs': logs, 'user': user, 'form': form}
        return render(request, 'activity_log.html', context)


class UserAccountView(LoginRequiredMixin, View):
    
    def get(self, request):
        user = request.user
        form = UpdateAccountDetailsForm(initial={
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
        })
        context = {
            'form': form,
            'user': user,
        }
        return render(request, 'recruiter/user_account.html', context)
    
    def post(self, request):
        form = UpdateAccountDetailsForm(request.POST)
        if form.is_valid():
            user = request.user
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()
            messages.success(request, 'Your account details have been successfully updated!')
            return redirect('recruiter_account')
        else:
            return render(request, 'recruiter/user_account.html', {'form': form})

class UpdatePasswordView(LoginRequiredMixin, FormView):
    template_name = 'recruiter/change_password.html'
    form_class = PasswordChangeForm
    success_url = reverse_lazy('recruiter_account')
    
    def get_form(self):
        form = super().get_form()
        for field in form.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        return form

    def get_form_kwargs(self):
        """Provide the current user to the form."""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        """Handle successful form submission."""
        form.save()
        update_session_auth_hash(self.request, form.user)  # Prevent logout after password change
        messages.success(self.request, 'Your password has been successfully updated!')
        return redirect(self.success_url)

    def form_invalid(self, form):
        """Handle form errors."""
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)
