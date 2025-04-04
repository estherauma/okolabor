from django.conf import settings
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.timezone import now
from django.utils.translation import gettext as _
from django.views import View
from django.views.generic.edit import FormView
from django.http import JsonResponse
from account.forms.account_update import UpdateAccountDetailsForm
from account.forms.filter_logs import UserLogsFilterForm
from django.utils import timezone
from django.utils.timezone import now
from account.models import UserNotification
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.models import Group
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.http import JsonResponse
import datetime
from account.models import User, UserNotification
from recruiting.models import WorkAssignment, Employer


class UserListView(LoginRequiredMixin, View):
    def get(self, request):
        users = User.objects.filter(groups__name='recruiter').values(
            'curp', 'email', 'first_name', 'last_name', 'created_at', 'is_active', 'language'
        )
        pending = User.objects.filter(
            is_active=False,
            groups__name='recruiter'
        ).values(
            'curp', 'email', 'first_name', 'last_name', 'created_at', 'is_active', 'language'
        )

        form = UpdateAccountDetailsForm() 
        language_choices = form.fields["language"].choices

        status_choices = [
            (True, "Active"),
            (False, "Inactive"),
        ]

        worker_assignments = WorkAssignment.objects.select_related('worker', 'role', 'work_request')
        workers = [
            {
                'curp': assignment.worker.curp,
                'email': assignment.worker.email,
                'first_name': assignment.worker.first_name,
                'last_name': assignment.worker.last_name,
                'role': assignment.role.title if assignment.role else 'No Role',
                'work_request': assignment.work_request.name if assignment.work_request else 'No Work Request',
                'status': assignment.status,
                'assigned_date': assignment.assigned_date
            }
            for assignment in worker_assignments if assignment.worker
        ]

        recruiter_admins = User.objects.filter(groups__name='recruiter_admin').values(
            'curp', 'email', 'first_name', 'last_name', 'created_at', 'is_active', 'language'
        )

        context = {
            'users': users, 
            'pending_users': pending,
            'language_choices': language_choices,
            'status_choices': status_choices,
            'workers': workers,
            'recruiter_admins': recruiter_admins,
            
            }
        return render(request, 'recruiter/manage_users.html', context)

    def post(self, request):
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        user_email = request.POST.get('email')
        curp = request.POST.get('curp')

        if not all([first_name, last_name, user_email, curp]):
            messages.error(request, _("addUserAllFieldsAreRequired."))
            return redirect('manage_users')

        user = User.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=user_email,
            curp=curp,
            is_active=True
        )

        recruiter_group, created = Group.objects.get_or_create(name='recruiter')
        user.groups.add(recruiter_group)


        token = PasswordResetTokenGenerator().make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        current_site = get_current_site(request)
        site_url = f"{request.scheme}://{current_site.domain}"
        invite_link = f"{site_url}{reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})}"

        email_subject = _("inviteEmailYou'reInvited!")
        email_body = render_to_string(
            'invite_email.html', 
            {
                'first_name': first_name,
                'invite_link': invite_link,
                'site_url': site_url
            }
        )

        email = EmailMessage(
            subject=email_subject,
            body=email_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user_email.strip()],
        )
        email.content_subtype = 'html'
        email_sent = email.send()
        if email_sent:
            messages.success(request, _("inviteEmailInvitationSentSuccessfully!"))
        else:
            messages.error(request, _("inviteEmailFailedToSendEmail."))

        return redirect('manage_users')

class UserActivitLogView(LoginRequiredMixin, View):
    def get(self, request):
        form = UserLogsFilterForm(request.GET)
        user = User.objects.get(pk=request.user.id)
        logs = user.audit_logs.all()

        if form.is_valid():
            filter_type = form.cleaned_data.get('date_filter_type')

            if filter_type == 'today':
                logs = logs.filter(created_at__date=timezone.now().date())
            elif filter_type == 'last_7_days':
                start_date = timezone.now().date() - timezone.timedelta(days=7)
                logs = logs.filter(created_at__date__gte=start_date)
            elif filter_type == 'this_month':
                start_date = timezone.now().date().replace(day=1)
                logs = logs.filter(created_at__date__gte=start_date)

        context = {'logs': logs, 'user': user, 'form': form}
        return render(request, 'activity_log.html', context)

class UserAccountView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        form = UpdateAccountDetailsForm(initial={
            'curp': user.curp,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'language': user.language,
        })

        context = {
            'form': form,
            'user': user,
        }
        return render(request, 'recruiter/user_account.html', context)

    def post(self, request):
        form = UpdateAccountDetailsForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save()
            messages.success(request, _('Your account details have been successfully updated!'))
            response = redirect('recruiter_account')
            if hasattr(user, 'language'):
                response.set_cookie(settings.LANGUAGE_COOKIE_NAME, user.language.lower())
            return response
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
        messages.success(self.request, _('Your password has been successfully updated!'))
        return redirect(self.success_url)

    def form_invalid(self, form):
        """Handle form errors."""
        messages.error(self.request, _('Please correct the errors below.'))
        return super().form_invalid(form)


class AccountNotificationsView(LoginRequiredMixin, View):
    template_name = 'account/notifications.html'

    def get(self, request):
        notifications = UserNotification.objects.filter(user=request.user).order_by('-created_at')
        notifications.filter(status='unread').update(status='read', read_at=now())
        context = {'notifications': notifications}
        return render(request, self.template_name,context)


def edit_user_view(request, curp):
    user = get_object_or_404(User, curp=curp)

    if request.method == "POST":
        form = UpdateAccountDetailsForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = form.cleaned_data["is_active"] == "True"  # Convert string to boolean
            user.save()
            messages.success(request, "User details updated successfully!")
            redirect_url = reverse("manage_users")
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({"success": True, "redirect_url": redirect_url})
            return redirect(redirect_url)
        else:
            return JsonResponse({"success": False, "error": form.errors}, status=400)
    else:
        form = UpdateAccountDetailsForm(instance=user)

    return render(request, "recruiter/recruiter_models/edit_user_modal.html", {"form": form, "user": user})