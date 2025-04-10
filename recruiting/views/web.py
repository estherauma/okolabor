from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import CreateView
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils.decorators import method_decorator
from django.contrib.auth.models import Group
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.http import HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect

from account.models import User
from recruiting.forms import (
    EmployerForm,
    OkoMessageCreateForm,
    OkoMessageFilterForm,
    RoleDeductionForm,
    RoleEmploymentLocationForm,
    RoleHoursForm,
    RoleHousingInformationForm,
    RoleMealProvision,
    RoleQualificationForm,
    RoleWagesForm,
    TodoFilterForm,
    WorkRequestForm,
    WorkRequestRoleForm,
)
from recruiting.models import (
    Deduction,
    Organization,
    EmploymentLocation,
    Hours,
    HousingInformation,
    MealProvision,
    OkoMessage,
    Qualification,
    Role,
    Wages,
    WorkRequests,
    EmployerRecruiter,
    WorkAssignment,
    EmployerContact
)

class EmployerListView(View):
    def get(self, request):
        print("EmployerListView")
        user = request.user
        query = request.GET.get('query')

        if user.groups.filter(name='admin').exists():
            employers_list = Organization.objects.all()
            print('admin employer list')
            print(len(employers_list))
        elif user.groups.filter(name='recruiter').exists():
            employers_list = Organization.objects.filter(employerrecruiter__recruiter=user).distinct()
        else:
            employers_list = Organization.objects.none()

        if query:
            employers_list = employers_list.filter(
                Q(name__icontains=query) |
                Q(email__icontains=query) |
                Q(address__icontains=query) |
                Q(country__icontains=query) |
                Q(phone__icontains=query)
            )

        paginator = Paginator(employers_list, len(employers_list))
        page_number = request.GET.get('page')
        employers = paginator.get_page(page_number)

        recruiter_group = Group.objects.get(id=1) 
        recruiters = recruiter_group.user_set.all()

        employers_data = []
        for employer in employers:
            assigned_recruiters = EmployerRecruiter.objects.filter(employer=employer)

            recruiter_names = list(set(rec.recruiter.get_full_name() for rec in assigned_recruiters if rec.recruiter == user))

            employers_data.append({
                'id': employer.id,
                'name': employer.name,
                'email': employer.email,
                'address': employer.address,
                'country': employer.country,
                'phone': employer.phone,
                'recruiters': recruiter_names
            })

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'employers': employers_data,
                'has_more': employers.has_next()
            })

        context = {'employers': employers_data, 'query': query,'recruiters': recruiters}
        return render(request, 'recruiting/employers/list.html', context)



class EmployerCreateView(CreateView):
    model = Organization
    form_class = EmployerForm
    template_name = 'recruiting/employers/create.html'

    def form_valid(self, form):
        messages.success(self.request, _('Employer created successfully'))
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
        employer = get_object_or_404(Organization, pk=pk)
        
        work_requests = WorkRequests.objects.filter(employer=employer)
        
        in_progress_work_requests = work_requests.filter(status__in=['Open', 'Requested'])
        closed_work_requests = work_requests.filter(status='Closed')
        draft_work_requests = work_requests.filter(status='Draft')

        recruiters = EmployerRecruiter.objects.filter(employer=employer).select_related('recruiter')
        contacts = employer.contacts.all()
        context = {
            'employer': employer,
            'in_progress_work_requests': in_progress_work_requests,
            'closed_work_requests': closed_work_requests,
            'draft_work_requests': draft_work_requests,
            'recruiters': recruiters,
            'contacts': contacts,
            'work_requests': work_requests
        }
        return render(request, 'recruiting/employers/detail.html', context)

class WorkRequestsListView(View):
    def get(self, request):
        user = request.user
        admin_group = Group.objects.get(name='admin')
        recruiter_group = Group.objects.get(name='recruiter')

        if admin_group in user.groups.all():
            work_requests = WorkRequests.objects.all()
        elif recruiter_group in user.groups.all():
            assigned_employers = EmployerRecruiter.objects.filter(recruiter=user).values_list("employer", flat=True)
            work_requests = WorkRequests.objects.filter(employer_id__in=assigned_employers)
        else:
            work_requests = WorkRequests.objects.none()

        context = {"work_requests": work_requests}
        return render(request, "recruiting/work_requests/list.html", context)


class WorkRequestCreateView(CreateView):
    model = WorkRequests
    form_class = WorkRequestForm
    template_name = 'recruiting/work_requests/create.html'

    def form_valid(self, form):
        messages.success(self.request, _('jobOrderCreatedSuccessfully'))
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
        active_workers = WorkAssignment.objects.filter(
            work_request=work_request, status__in=['Assigned', 'Accepted']
        ).select_related('worker')
        context = {
            'workrequest': work_request,
            'active_workers': active_workers,
        }
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
        messages.success(self.request, _('addRoleRoleCreatedSuccessfully'))
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

class RecruiterListView(LoginRequiredMixin, View):
    def get(self, request):
        if not request.user.groups.filter(name='recruiter_admin').exists():
            return redirect('recruiting_web:access_denied')

        recruiters = User.objects.filter(groups__name='recruiter').prefetch_related('employerrecruiter_set__employer')
        employers = Organization.objects.all()

        recruiter_data = []
        for recruiter in recruiters:
            assigned_employers = recruiter.employerrecruiter_set.all()
            employer_names = ", ".join([employer_recruiter.employer.name for employer_recruiter in assigned_employers])

            recruiter_data.append({
                "recruiter": recruiter,
                "employer_names": employer_names if employer_names else "Not Assigned any person"
            })
        return render(request, 'recruiting/recruiters/list.html', {'recruiters': recruiter_data, 'employers': employers})
    

class AddRecruiterToEmployerView(LoginRequiredMixin, View):
    def post(self, request, employer_id, recruiter_id):

        if not request.user.groups.filter(name='recruiter_admin').exists():
            return redirect('recruiting_web:access_denied')

        employer = get_object_or_404(Organization, id=employer_id)
        recruiter = get_object_or_404(User, id=recruiter_id)

        employer_recruiter, created = EmployerRecruiter.objects.get_or_create(employer=employer, recruiter=recruiter)

        if created:
            messages.success(request, _("Recruiter {email} assigned to {employer}.").format(email=recruiter.email, employer=employer.name))
        else:
            messages.info(request, _("Recruiter {email} is already assigned to {employer}.").format(email=recruiter.email, employer=employer.name))

        return redirect('recruiting_web:recruiter_list')


class RemoveRecruiterFromEmployerView(LoginRequiredMixin, View):
    def post(self, request, employer_id, recruiter_id):

        if not request.user.groups.filter(name='recruiter_admin').exists():
            return redirect('recruiting_web:access_denied')

        employer = get_object_or_404(Organization, id=employer_id)
        recruiter = get_object_or_404(User, id=recruiter_id)

        num_deleted, deleted_info = EmployerRecruiter.objects.filter(employer=employer, recruiter=recruiter).delete()

        if num_deleted > 0:
            messages.success(request, _("Recruiter {email} removed from {employer}.").format(email=recruiter.email, employer=employer.name))
        else:
            messages.info(request, _("Recruiter {email} was already removed from {employer}.").format(email=recruiter.email, employer=employer.name))

        return redirect('recruiting_web:recruiter_list')

            

class AccessDeniedView(View):
    def get(self, request):
        return render(request, 'recruiting/access_denied.html')



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
        messages.success(self.request, _('roleAddHoursRoleHoursSuccessfullyAdded'))
        return super().form_valid(form)


class RoleWagesCreateView(RoleDataBaseView):
    model = Wages
    form_class = RoleWagesForm
    template_name = 'recruiting/work_requests/create_wages.html'

    def form_valid(self, form):
        messages.success(self.request, _('roleWagesRolesWagesSuccessfullyAdded'))
        return super().form_valid(form)


class RoleDeductionsCreateView(RoleDataBaseView):
    model = Deduction
    form_class = RoleDeductionForm
    template_name = 'recruiting/work_requests/create_deductions.html'

    def form_valid(self, form):
        messages.success(self.request, _('roleDeductionsRolesDeductionsSuccessfullyAdded'))
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
        messages.success(self.request, _('roleEmploymentLocationSuccessfullyAddedRoleLocation'))
        return super().form_valid(form)


class RoleHousingCreateView(RoleDataBaseView):
    model = HousingInformation
    form_class = RoleHousingInformationForm
    template_name = 'recruiting/work_requests/create_housing_info.html'

    def form_valid(self, form):
        messages.success(
            self.request,
            _('roleHousingInformationSuccessfullyAddedRoleHousingInformation')
        )
        return super().form_valid(form)


class RoleMealsCreateView(RoleDataBaseView):
    model = MealProvision
    form_class = RoleMealProvision
    template_name = 'recruiting/work_requests/create_meal_provision.html'

    def form_valid(self, form):
        messages.success(self.request,
                         _('roleMealProvisionSuccessfullyAddedRoleMealsInformation'))
        return super().form_valid(form)


class RecruiterTodoView(LoginRequiredMixin, View):
    def get(self, request):
        # initialize filter form
        form = TodoFilterForm()
        user = User.objects.get(pk=request.user.id)
        todos = WorkRequests.objects.exclude(
            status='completed'
        )
        context = {'todos': todos, 'user': user, 'form': form}
        return render(request, 'recruiting/todo.html', context)


class OkoMessageListView(View):
    def get(self, request):
        form = OkoMessageFilterForm()
        items = OkoMessage.objects.all()
        context = {'items': items, 'form': form }
        return render(request, 'recruiting/messages/list.html', context)


class OkoMessageCreateView(CreateView):
    model = OkoMessage
    form_class = OkoMessageCreateForm
    template_name = 'recruiting/messages/create.html'

    def form_valid(self, form):
        messages.success(self.request, _('messageCreatedSuccessfully'))
        return super(OkoMessageCreateView, self).form_valid(form)

    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{field}: {error}')
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse(
            'recruiting_web:recruiter_messages'
        )

class OkoMessageDetailsView(View):
    def get(self, request,id):
        message = get_object_or_404(OkoMessage, pk=id)
        context = {'message': message}
        return render(request, 'recruiting/messages/details.html',context)
    
class AssignRecruiterView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            employer_ids = data.get("employer_ids", [])
            recruiter_id = data.get("recruiter_id")

            if not employer_ids or not recruiter_id:
                return JsonResponse({"success": False, "error": "invalidDataProvidedMissingEmployerIdsOrRecruiterId."}, status=400)

            recruiter_group = Group.objects.filter(name="Recruiter").first()
            if not recruiter_group:
                return JsonResponse({"success": False, "error": "recruiterGroupNotFound."}, status=404)

            recruiter = recruiter_group.user_set.filter(id=recruiter_id).first()
            if not recruiter:
                return JsonResponse({"success": False, "error": "recruiterNotFoundInRecruiterGroup."}, status=404)

            assigned_employers = []
            not_found_employers = []

            for employer_id in employer_ids:
                try:
                    employer = Organization.objects.get(id=employer_id)
                    obj, created = EmployerRecruiter.objects.get_or_create(
                        employer=employer, recruiter=recruiter
                    )
                    assigned_employers.append(employer_id)
                except ObjectDoesNotExist:
                    not_found_employers.append(employer_id)

            response_data = {
                "success": True,
                "message": f"successfullyAssignedRecruiterTo{len(assigned_employers)}Employers.",
                "assignedEmployers": assigned_employers,
                "notFoundEmployers": not_found_employers,
            }

            if not_found_employers:
                response_data["warning"] = f"employersWithIds{not_found_employers}NotFound."

            return JsonResponse(response_data)

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "invalidJsonFormat."}, status=400)

        except Exception as e:
            return JsonResponse({"success": False, "error": f"anErrorOccurred{str(e)}"}, status=500)

    
    
@method_decorator(csrf_exempt, name='dispatch')
class SendRecruiterEmailView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            employer_ids = data.get("employer_ids", [])
            recruiter_id = data.get("recruiter_id")

            if not employer_ids or not recruiter_id:
                return JsonResponse({"success": False, "error": "invalidJsonFormatMissingEmployerIdsOrRecruiterId."}, status=400)

            recruiter_group = Group.objects.filter(id=1).first()
            if not recruiter_group:
                return JsonResponse({"success": False, "error": "recruiterGroupNotFound."}, status=404)

            recruiters = recruiter_group.user_set.filter(id=recruiter_id)
            if not recruiters.exists():
                return JsonResponse({"success": False, "error": "recruiterNotFoundInGroup."}, status=404)

            recruiter = recruiters.first()

            for employer_id in employer_ids:
                employer = get_object_or_404(Organization, id=employer_id)
                encoded_employer_id = urlsafe_base64_encode(force_bytes(employer.id))
                encoded_recruiter_id = urlsafe_base64_encode(force_bytes(recruiter.id))

                accept_url = request.build_absolute_uri(
                    reverse("recruiting_web:accept_recruiter", args=[encoded_employer_id, encoded_recruiter_id])
                )
                reject_url = request.build_absolute_uri(
                    reverse("recruiting_web:reject_recruiter", args=[encoded_employer_id, encoded_recruiter_id])
                )

                subject = "recruiterAssignmentRequest"
                message = f"""
                Hi {recruiter.first_name},

                You have been requested to be assigned as a recruiter for {employer.name}.

                Please choose an option:
                Accept: {accept_url}
                Reject: {reject_url}

                Regards,
                Team
                """

                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recruiter.email])

            return JsonResponse({"success": True, "message": "emailsSentSuccessfully."})

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "invalidJsonFormat."}, status=400)
        
        except Exception as e:
            return JsonResponse({"success": False, "error": f"anErrorOccurred{str(e)}"}, status=500)

class AcceptRecruiterView(View):
    def get(self, request, employer_id, recruiter_id, *args, **kwargs):
        try:
            employer_id = force_str(urlsafe_base64_decode(employer_id))
            recruiter_id = force_str(urlsafe_base64_decode(recruiter_id))

            employer = get_object_or_404(Organization, id=employer_id)
            recruiter = get_object_or_404(User, id=recruiter_id)

            obj, created = EmployerRecruiter.objects.get_or_create(employer=employer, recruiter=recruiter)

            subject = "recruiterAssignmentAccepted"
            message = f"""
            Hi {recruiter.first_name},

            You have been assigned as a recruiter for {employer.name}.

            Regards,
            Team
            """
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recruiter.email])

            messages.success(request, _("recruiterAssignmentAcceptedSuccessfully."))
            return JsonResponse({"success": True, "message": "recruiterAssignmentAcceptedSuccessfully."})

        except Organization.DoesNotExist:
            return JsonResponse({"success": False, "error": "employerNotFound."}, status=404)

        except User.DoesNotExist:
            return JsonResponse({"success": False, "error": "recruiterNotFound."}, status=404)

        except Exception as e:
            messages.error(request, f"anErrorOccurred_{str(e)}")
            return JsonResponse({"success": False, "error": f"anErrorOccurred_{str(e)}"}, status=500)

class RejectRecruiterView(View):
    def get(self, request, employer_id, recruiter_id, *args, **kwargs):
        try:
            employer_id = force_str(urlsafe_base64_decode(employer_id))
            recruiter_id = force_str(urlsafe_base64_decode(recruiter_id))

            employer = get_object_or_404(Organization, id=employer_id)
            recruiter = get_object_or_404(User, id=recruiter_id)


            messages.success(request, _("recruiterAssignmentRejectedSuccessfully."))
            return JsonResponse({"success": True, "message": "recruiterAssignmentRejectedSuccessfully."})

        except Organization.DoesNotExist:
            return JsonResponse({"success": False, "error": "employerNotFound."}, status=404)

        except User.DoesNotExist:
            return JsonResponse({"success": False, "error": "recruiterNotFound."}, status=404)

        except Exception as e:
            messages.error(request, f"anErrorOccurred_{str(e)}")
            return JsonResponse({"success": False, "error": f"anErrorOccurred_{str(e)}"}, status=500)


class RemoveWorkerFromAssignmentView(View):
    def get(self, request, *args, **kwargs):
        try:
            worker_id = kwargs.get('worker_id')
            assignment = get_object_or_404(WorkAssignment, worker__id=worker_id)
            work_request_id = assignment.work_request.pk  
            
            assignment.status = 'Deleted'
            assignment.save()

            messages.success(request, _("WorkerAssignmentSuccessfullyMarkedAsDeleted."))
        
        except Exception as e:
            messages.error(request, f"errorRemovingWorker_{str(e)}")
            return redirect(reverse('recruiting_web:workrequest_list'))

        return redirect(reverse('recruiting_web:workrequest_detail', kwargs={'pk': work_request_id}))

@method_decorator(csrf_exempt, name='dispatch')
class UpdateStatusView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            work_requests = data.get('work_requests', [])
            status = data.get('status', '')
            
            if work_requests and status:
                updated_count = WorkRequests.objects.filter(id__in=work_requests).update(status=status)
                if updated_count > 0:
                    messages.success(request, _("workRequestsSuccessfullyUpdatedTo'{}'Status.").format(status))
                    return JsonResponse({'success': True, 'message': f"workRequestsSuccessfullyUpdatedTo'{status}'Status."})
                else:
                    messages.error(request, _("noWorkRequestsFoundToUpdate."))
                    return JsonResponse({'success': False, 'message': 'noWorkRequestsFoundtoUpdate.'})
            messages.error(request, _("invalidDataProvided."))
            return JsonResponse({'success': False, 'message': 'invalidDataProvided.'})

        except json.JSONDecodeError:
            messages.error(request, "invalidJSONData.")
            return JsonResponse({'success': False, 'message': 'invalidJSONData.'})


class ContactWorkRequestsView(View):
    def get(self, request, contact_id):
        contact = get_object_or_404(EmployerContact, id=contact_id)
        employer = contact.employer 
        recruiters = EmployerRecruiter.objects.filter(employer=employer).select_related('recruiter')
        work_requests = WorkRequests.objects.filter(employer=employer)
        in_progress_work_requests = work_requests.filter(status__in=['Open', 'Requested'])
        closed_work_requests = work_requests.filter(status='Closed')
        draft_work_requests = work_requests.filter(status='Draft')

        context = {
            'contact': contact,
            'employer': employer,
            'in_progress_work_requests': in_progress_work_requests,
            'closed_work_requests': closed_work_requests,
            'draft_work_requests': draft_work_requests,
            'work_requests': work_requests,
            'recruiters': recruiters,
        }

        return render(request, 'recruiting/work_requests/workrequest_details.html', context)
    
@method_decorator(csrf_exempt, name='dispatch')
class AssignEmployerContactView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            employer_id = data.get("employer_id")
            name = data.get("name")
            email = data.get("email")
            phone = data.get("phone")
            position = data.get("position", "")
            is_primary = data.get("is_primary")

            # Check if employer ID is missing
            if not employer_id:
                messages.error(request, "employerIDIsRequired.")
                return JsonResponse({'error': 'employerIDIsRequired.'}, status=400)

            # Check if the email already exists
            if EmployerContact.objects.filter(email=email).exists():
                messages.error(request, "Email already exists.")
                return JsonResponse({'error': 'emailAlreadyExists.'}, status=400)

            try:
                employer = Employer.objects.get(id=employer_id)
            except Employer.DoesNotExist:
                messages.error(request, "Employer not found.")
                return JsonResponse({'error': 'employerNotFound.'}, status=404)

            # Create the contact
            EmployerContact.objects.create(
                employer=employer,
                name=name,
                email=email,
                phone=phone,
                position=position,
                is_primary=is_primary
            )

            messages.success(request, _("ContactAssignedSuccessfully!"))
            return JsonResponse({'success': True, 'message': 'ContactAssignedSuccessfully!'})

        except Exception as e:
            messages.error(request, str(e))
            return JsonResponse({'error': str(e)}, status=500)

    def get(self, request, *args, **kwargs):
        messages.error(request, "GET not allowed")
        return JsonResponse({'error': 'GET not allowed.'}, status=405)
