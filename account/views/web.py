from django.conf import settings
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
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
from django.views.generic.edit import FormView,CreateView
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
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.views.generic import ListView
from django.views.generic.detail import DetailView
import datetime
import json
from account.models import User, UserNotification,Log
from recruiting.models import WorkAssignment,Organization
from recruiting.forms import WorkerCreateForm,RecruiterAdminCreateForm,EmployerForm


class UserListView(LoginRequiredMixin, View):
    def get(self, request):
        

        form = UpdateAccountDetailsForm() 
        form_worker_class = WorkerCreateForm()
        form_recruiter_admin_class = RecruiterAdminCreateForm()
        language_choices = form.fields["language"].choices

        status_choices = [
            (True, "Active"),
            (False, "Inactive"),
        ]

        workers_list = User.objects.filter(groups__name='worker').values(
            'curp', 'email', 'first_name', 'last_name', 'created_at', 'is_active', 'language'
        )

        
        recruiter_organizations = Organization.objects.filter(type='recruiter').values(
            'id', 'name', 'email', 'phone', 'website', 'address', 'city', 'state', 'country', 'zip_code', 'type', 'is_active'
        )

        employer_organizations = Organization.objects.filter(type='employer').values(
            'id', 'name', 'email', 'phone', 'website', 'address', 'city', 'state', 'country', 'zip_code', 'type', 'is_active'
        )

        recruiters = list(User.objects.filter(groups__name='recruiter').values(
            'id','curp', 'email', 'first_name', 'last_name', 'created_at', 'is_active', 'language'
        ))
        for r in recruiters:
            r['group'] = 'recruiter'

        recruiter_admins = list(User.objects.filter(groups__name='recruiter_admin').values(
            'id','curp', 'email', 'first_name', 'last_name', 'created_at', 'is_active', 'language'
        ))
        for ra in recruiter_admins:
            ra['group'] = 'recruiter_admin'

        employer = list(User.objects.filter(groups__name='employer').values(
            'id','curp', 'email', 'first_name', 'last_name', 'created_at', 'is_active', 'language'
        ))
        for ra in employer:
            ra['group'] = 'employer'

        employer_admin = list(User.objects.filter(groups__name='employer_admin').values(
            'id','curp', 'email', 'first_name', 'last_name', 'created_at', 'is_active', 'language'
        ))
        for ra in employer_admin:
            ra['group'] = 'employer_admin'

        combined_users = recruiters + recruiter_admins
        combined_employer = employer + employer_admin

        context = {
            'users': combined_users, 
            'language_choices': language_choices,
            'status_choices': status_choices,
            'workers': workers_list,
            'form_worker_class': form_worker_class,
            'form_recruiter_admin_class': form_recruiter_admin_class,
            'employers_list': combined_employer,
            'recruiter_organizations': recruiter_organizations,
            'employer_organizations': employer_organizations,
            
            }
        return render(request, 'recruiter/manage_users.html', context)

    def post(self, request):
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        user_email = request.POST.get('email')
        curp = request.POST.get('curp')
        role = request.POST.get('role')

        if not all([first_name, last_name, user_email, curp, role]):
            messages.error(request, _("addUserAllFieldsAreRequired."))
            return redirect('manage_users')

        user = User.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=user_email,
            curp=curp,
            is_active=True
        )

        if role in ['recruiter', 'recruiter_admin','employer', 'employer_admin']:
            group, created = Group.objects.get_or_create(name=role)
            user.groups.add(group)

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
            messages.success(request, _('accountUpdateSuccess'))
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
        messages.success(self.request, _('changePasswordYourPasswordHasBeenSuccessfullyUpdated!'))
        return redirect(self.success_url)

    def form_invalid(self, form):
        """Handle form errors."""
        messages.error(self.request, _('changePasswordPleaseCorrectTheErrorsBelow.'))
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
            user.is_active = form.cleaned_data["is_active"]
            user.save()

            group_name = form.cleaned_data.get("group")
            if group_name:
                user.groups.clear()
                group, _ = Group.objects.get_or_create(name=group_name)
                user.groups.add(group)

            messages.success(request, "UserDetailsUpdatedSuccessfully!")
            redirect_url = reverse("manage_users")
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({"success": True, "redirect_url": redirect_url})
            return redirect(redirect_url)
        else:
            return JsonResponse({"success": False, "error": form.errors}, status=400)
    else:
        form = UpdateAccountDetailsForm(instance=user)

    return render(request, "recruiter/recruiter_models/edit_recruiter_modal.html", {"form": form, "user": user})


def edit_employer_view(request, curp):
    user = get_object_or_404(User, curp=curp)

    if request.method == "POST":
        form = UpdateAccountDetailsForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = form.cleaned_data["is_active"]
            user.save()

            group_name = form.cleaned_data.get("group")
            if group_name:
                user.groups.clear()
                group, _ = Group.objects.get_or_create(name=group_name)
                user.groups.add(group)

            messages.success(request, "UserDetailsUpdatedSuccessfully!")
            redirect_url = reverse("manage_users")
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({"success": True, "redirect_url": redirect_url})
            return redirect(redirect_url)
        else:
            return JsonResponse({"success": False, "error": form.errors}, status=400)
    else:
        form = UpdateAccountDetailsForm(instance=user)

    return render(request, "employers/edit_employer_modal.html", {"form": form, "user": user})

def edit_worker(request, curp):
    if request.method == 'POST':
        user = get_object_or_404(User, curp=curp)

        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.is_active = request.POST.get('is_active')
        user.language = request.POST.get('language')
        user.save()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})

        messages.success(request, _('WorkerUpdatedSuccessfully.'))
        return redirect('manage_users')

    return redirect('manage_users')

class WorkerModalCreateView(View):
    def post(self, request, *args, **kwargs):
        form = WorkerCreateForm(request.POST)
        if form.is_valid():
            worker = form.save()
            try:
                worker_group = Group.objects.get(name='worker')
                worker.groups.add(worker_group)
            except Group.DoesNotExist:
                messages.error(request, _("WorkerGroupDoesNotExistPleaseCreateIt."))
                return redirect('manage_users')
                
            messages.success(request, _("workerCreatedSuccessfully."))
            return redirect('manage_users')
        else:
            messages.error(request, _("pleaseCorrectTheErrorsInTheForm"))
            return redirect('manage_users')
        

class RecruiterAdminModalCreateView(View):
    def post(self, request, *args, **kwargs):
        form = RecruiterAdminCreateForm(request.POST)
        if form.is_valid():
            recruiter = form.save()
            try:
                recruiter_group = Group.objects.get(name='recruiter_admin')
                recruiter.groups.add(recruiter_group)
            except Group.DoesNotExist:
                messages.error(request, _("recruiterAdminGroupDoesNotExistPleaseCreateIt."))
                return redirect('manage_users')

            messages.success(request, _("recruiterAdminCreatedSuccessfully."))
            return redirect('manage_users')
        else:
            messages.error(request, _("pleaseCorrectTheErrorsInTheForm."))
            return redirect('manage_users')
        

class OrganizationCreateView(UserPassesTestMixin, CreateView):
    model = Organization
    form_class = EmployerForm
    template_name = 'organization/create_organization.html'

    def test_func(self):
        return self.request.user.is_superuser

    def form_valid(self, form):
        messages.success(self.request, _('organizationCreatedSuccessfully'))
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{field}: {error}')
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse(
            'recruiting_web:employer_detail',
            kwargs={'pk': self.object.pk}
        )
    
def edit_organization(request, organization_id):
    if request.method == 'POST':
        organization = get_object_or_404(Organization, pk=organization_id)

        organization.name = request.POST.get('name')
        organization.email = request.POST.get('email')
        organization.phone = request.POST.get('phone')
        organization.website = request.POST.get('website')
        organization.address = request.POST.get('address')
        organization.city = request.POST.get('city')
        organization.state = request.POST.get('state')
        organization.country = request.POST.get('country')
        organization.zip_code = request.POST.get('zip_code')
        organization.type = request.POST.get('type')
        organization.is_active = request.POST.get('is_active')
        organization.save()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})

        messages.success(request, _('organizationUpdatedSuccessfully.'))
        return redirect('recruiting_web:employer_detail', pk=organization.pk)

    return redirect('recruiting_web:employer_detail', pk=organization_id)

@require_POST
def assign_organization(request):
    org_id = request.POST.get("organization_id")
    selected_users = request.POST.get("selected_users")
    
    try:
        selected_users = json.loads(selected_users or "[]")
    except json.JSONDecodeError:
        messages.error(request, _("invalidUserSelection."))
        return JsonResponse({"success": False, "error": _("invalidUserSelection")})

    if not org_id or not selected_users:
        messages.error(request, _("pleaseSelectUsersAndanOrganization."))
        return JsonResponse({"success": False, "error": _("pleaseSelectUsersAndAnOrganization.")})

    org = get_object_or_404(Organization, id=org_id)
    users = User.objects.filter(id__in=selected_users)

    if not users.exists():
        messages.error(request, _("noValidUsersSelected."))
        return JsonResponse({"success": False, "error": _("noValidUsersSelected.")})

    try:
        for user in users:
            user.organizations.add(org)
        messages.success(request, _("Organization assigned successfully to selected users."))
        return JsonResponse({"success": True, "message": _("Organization assigned successfully to selected users.")})
    except Exception as e:
        messages.error(request, _("failedToAssignOrganization: ") + str(e))
        return JsonResponse({"success": False, "error": _("failedToAssignOrganization: ") + str(e)})

class LogListView(LoginRequiredMixin, ListView):
    model = Log
    template_name = 'userlogs/logs.html'
    context_object_name = 'logs'

    def get_queryset(self):
        user = self.request.user
        base_query = Log.objects.all()
        orgs = user.organizations.all() 


        if user.groups.filter(name='recruiter_admin').exists():
            base_query = base_query.filter(
                Q(user__organizations__in=orgs) & 
                Q(user__groups__name__in=['recruiter', 'recruiter_admin'])
            ).distinct()

        elif user.groups.filter(name='employer_admin').exists():
            base_query = base_query.filter(
                Q(user__organizations__in=orgs) & 
                Q(user__groups__name__in=['employer', 'employer_admin'])
            ).distinct()

        elif user.groups.filter(name='recruiter').exists():
            base_query = base_query.filter(user=user)

        elif user.groups.filter(name='employer').exists():
            base_query = base_query.filter(user=user)

        elif not user.groups.filter(name='admin').exists():
            base_query = base_query.filter(user=user)

        return base_query.exclude(
            content_type__model__in=['session', 'logentry']
        ).order_by('-timestamp')

class LogDetailView(LoginRequiredMixin, DetailView):
    model = Log
    template_name = 'userlogs/log_detail.html'
    context_object_name = 'log'

