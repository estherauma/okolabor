
# create modelform for Employer model
from django import forms
from django.utils.translation import gettext_lazy as _ 
from account.models import User
from recruiting.models import (
    Deduction, Organization, Hours, OkoMessage, Qualification,
    EmploymentLocation, HousingInformation, MealProvision,
    Role, Wages, WorkRequests,WorkAssignment
)

from account.models import (UserWorkExperience)
class EmployerForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ['name', 'email', 'phone', 'website',
                  'address', 'city', 'state', 'country',
                  'zip_code', 'description', 'type'
                  ]

        labels = {
            'name': _('createEmployerName'),
            'email': _('createEmployerEmail'),
            'phone': _('createEmployerTelephone'),
            'website': _('createEmployerWebsite'),
            'address': _('createEmployerAddress'),
            'city': _('createEmployerCity'),
            'state': _('createEmployerState'),
            'country': _('createEmployerCountry'),
            'zip_code': _('createEmployerZipCode'),
            'description': _('createEmployerDescription'),
            'type': _('OrganizationType'),
        }

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'website': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(EmployerForm, self).__init__(*args, **kwargs)
        self.fields['type'].initial = 'recruiter'


class WorkRequestForm(forms.ModelForm):
    class Meta:
        model = WorkRequests
        fields = [
            'name', 'start_date', 'end_date',
            'required_workers', 'employer', 'status'
        ]
        
        labels = {
            'name': _("createWorkRequestName"),
            'start_date': _("createWorkRequestStartDate"),
            'end_date': _("createWorkRequestEndDate"),
            'required_workers': _("createWorkRequestRequiredWorkers"),
            'employer': _("createWorkRequestEmployer"),
            'status': _("createWorkRequestStatus"),
        }

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'required_workers': forms.NumberInput(attrs={
                'class': 'form-control',
            }),
            'employer': forms.Select(attrs={
                'class': 'form-control',
            }),
            'status': forms.Select(attrs={
                'class': 'form-control',
            }),
        }

class WorkerAssignmentForm(forms.ModelForm):
    work_request = forms.ModelMultipleChoiceField(
        queryset=WorkRequests.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        label=_("Work Request")
    )

    class Meta:
        model = WorkAssignment
        fields = ['work_request', 'worker', 'status']

        labels = {
            'worker': _("Worker"),
            'status': _("Status"),
        }

        widgets = {
            'worker': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }



class WorkRequestRoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = [
            'title', 'usdol_case_number', 'work_type',
            'number_of_required_workers', 'work_request', 'description'
        ]
        
        labels = {
            'title': _('addRoleTitle'),
            'usdol_case_number': _('addRoleUsdolCaseNumber'),
            'work_type': _('addRoleWorkType'),
            'number_of_required_workers': _('addRoleNumberOfRequiredWorkers'),
            'work_request': _('addRoleWorkRequest'),
            'description': _('addRoleDescription'),
        }  

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'usdol_case_number': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'work_type': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'number_of_required_workers': forms.NumberInput(attrs={
                'class': 'form-control',
            }),
            'work_request': forms.Select(attrs={
                'class': 'form-control',
                'readonly': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
            }),
        }


class RoleHoursForm(forms.ModelForm):
    class Meta:
        model = Hours
        fields = [
            'role',
            'on_call',
            'estimate_weekly_hours',
            'sunday_hours',
            'monday_hours',
            'tuesday_hours',
            'wednesday_hours',
            'thursday_hours',
            'friday_hours',
            'saturday_hours',
            'job_description']
        
        labels = {
            'role': _('roleAddHoursRole'),
            'on_call': _('roleAddHoursOnCall'),
            'estimate_weekly_hours': _('roleAddHoursEstimatedWeeklyHours'),
            'sunday_hours': _('roleAddHoursSundayHours'),
            'monday_hours': _('roleAddHoursMondayHours'),
            'tuesday_hours': _('roleAddHoursTuesdayHours'),
            'wednesday_hours': _('roleAddHoursWednesdayHours'),
            'thursday_hours': _('roleAddHoursThursdayHours'),
            'friday_hours': _('roleAddHoursFridayHours'),
            'saturday_hours': _('roleAddHoursSaturdayHours'),
            'job_description': _('roleAddHoursJobDescription'),
        }
        
        widgets = {
            'role': forms.Select(attrs={
                'class': 'form-control',
                'readonly': True
            }),
            'on_call': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'type': 'checkbox'
            }),
            'estimate_weekly_hours': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'sunday_hours': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'monday_hours': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'tuesday_hours': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'wednesday_hours': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'thursday_hours': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'friday_hours': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'saturday_hours': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'job_description': forms.Textarea(attrs={
                'class': 'form-control',
            }),
        }


class RoleWagesForm(forms.ModelForm):
    class Meta:
        model = Wages
        fields = [
            'role', 'wage', 'wage_type', 'piece_rate_offerings',
            'piece_rate_offerings_type', 'frequency_of_pay',
            'details'
        ]
        
        labels = {
            'role': _('roleWagesRole'),
            'wage': _('roleWagesWage'),
            'wage_type': _('roleWagesWageType'),
            'piece_rate_offerings': _('roleWagesPieceRateOfferings'),
            'piece_rate_offerings_type': _('roleWagesPieceRateOfferingsType'),
            'frequency_of_pay': _('roleWagesFrequencyOfPay'),
            'details': _('roleWagesDetails'),
        }

        widgets = {
            'role': forms.Select(attrs={
                'class': 'form-control',
                'readonly': True
            }),
            'wage': forms.NumberInput(attrs={
                'class': 'form-control',
            }),
            'wage_type': forms.Select(attrs={
                'class': 'form-control',
            }),
            'piece_rate_offerings': forms.NumberInput(attrs={
                'class': 'form-control',
            }),
            'piece_rate_offerings_type': forms.Select(attrs={
                'class': 'form-control',
            }),
            'frequency_of_pay': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'details': forms.TextInput(attrs={
                'class': 'form-control',
            }),
        }


class RoleDeductionForm(forms.ModelForm):
    class Meta:
        model = Deduction
        fields = ['role', 'description', 'deduction_amount']
        
        labels = {
            'role': _('roleDeductionsRole'),
            'description': _('roleDeductionsDescription'),
            'deduction_amount': _('roleDeductionsDeductionAmount'),
        }

        widgets = {
            'role': forms.Select(attrs={
                'class': 'form-control',
                'readonly': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
            }),
            'deduction_amount': forms.NumberInput(attrs={
                'class': 'form-control',
            }),
        }


class RoleQualificationForm(forms.ModelForm):
    class Meta:
        model = Qualification
        fields = [
            'role',
            'minimum_education_requirement',
            'experience_required',
            'number_of_months_experience_required',
            'training_required',
            'number_of_months_training_required',
            'certification_license_requirements',
            'drug_screen',
            'lifting_requirements',
            'lifting_requirement_weight',
            'exposure_to_temperature',
            'extensive_pushing_or_pulling',
            'extensive_sitting_or_walking',
            'frequent_stooping_or_bending_over',
            'repetitive_movements',
            'support_of_other_employees',
            'other_qualifications']
        
        labels = {
            'role': _('roleQualificationRole'),
            'minimum_education_requirement': _('roleQualificationMinimumEducationRequirement'),
            'experience_required': _('roleQualificationExperienceRequired'),
            'number_of_months_experience_required': _('roleQualificationNumberOfMonthsExperienceRequired'),
            'training_required': _('roleQualificationTrainingRequired'),
            'number_of_months_training_required': _('roleQualificationNumberOfMonthsTrainingRequired'),
            'certification_license_requirements': _('roleQualificationCertification/LicenseRequirements'),
            'drug_screen': _('roleQualificationDrugScreen'),
            'lifting_requirements': _('roleQualificationLiftingRequirements'),
            'lifting_requirement_weight': _('roleQualificationLiftingRequirementWeight'),
            'exposure_to_temperature': _('roleQualificationExposureToTemperature'),
            'extensive_pushing_or_pulling': _('roleQualificationExtensivePushingOrPulling'),
            'extensive_sitting_or_walking': _('roleQualificationExtensiveSittingOrWalking'),
            'frequent_stooping_or_bending_over': _('roleQualificationFrequentStoopingOrBendingOver'),
            'repetitive_movements': _('roleQualificationRepetitiveMovements'),
            'support_of_other_employees': _('roleQualificationSupportOfOtherEmployees'),
            'other_qualifications': _('roleQualificationOtherQualifications'),
        }

        widgets = {
            'role': forms.Select(attrs={
                'class': 'form-control',
                'readonly': True
            }),
            'minimum_education_requirement': forms.Select(attrs={
                'class': 'form-control',
            }),
            'experience_required': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'number_of_months_experience_required': forms.NumberInput(attrs={
                'class': 'form-control',
            }),
            'training_required': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'number_of_months_training_required': forms.NumberInput(attrs={
                'class': 'form-control',
            }),
            'certification_license_requirements': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'drug_screen': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'lifting_requirements': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'lifting_requirement_weight': forms.NumberInput(attrs={
                'class': 'form-control',
            }),
            'exposure_to_temperature': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'extensive_pushing_or_pulling': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'extensive_sitting_or_walking': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'frequent_stooping_or_bending_over': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'repetitive_movements': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'support_of_other_employees': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'support_of_other_employees_number': forms.NumberInput(attrs={
                'class': 'form-control',
            }),
            'other_qualifications': forms.Textarea(attrs={
                'class': 'form-control',
            }),
        }


class RoleEmploymentLocationForm(forms.ModelForm):
    class Meta:
        model = EmploymentLocation
        fields = [
            'role', 'address', 'city', 'county', 'state',
            'postal_code', 'additional_info', 'role'
        ]
        
        labels = {
            'role': _('roleEmploymentLocationRole'),
            'address': _('roleEmploymentLocationAddress'),
            'city': _('roleEmploymentLocationCity'),
            'county': _('roleEmploymentLocationCounty'),
            'state': _('roleEmploymentLocationState'),
            'postal_code': _('roleEmploymentLocationPostalCode'),
            'additional_info': _('roleEmploymentLocationAdditionalInfo'),
        }
        
        widgets = {
            'role': forms.Select(attrs={
                'class': 'form-control',
                'readonly': True
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'county': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'additional_info': forms.Textarea(attrs={
                'class': 'form-control',
            }),
        }


class RoleHousingInformationForm(forms.ModelForm):
    class Meta:
        model = HousingInformation
        fields = [
            'role', 'address', 'city', 'county', 'state',
            'postal_code', 'type_of_housing', 'additional_info'
        ]
        
        labels = {
            'role': _('roleHousingInformationRole'),
            'address': _('roleHousingInformationAddress'),
            'city': _('roleHousingInformationCity'),
            'county': _('roleHousingInformationCounty'),
            'state': _('roleHousingInformationState'),
            'postal_code': _('roleHousingInformationPostalCode'),
            'type_of_housing': _('roleHousingInformationTypeOfHousing'),
            'additional_info': _('roleHousingInformationAdditionalInfo'),
        }
        
        widgets = {
            'role': forms.Select(attrs={
                'class': 'form-control',
                'readonly': True
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'county': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'type_of_housing': forms.Select(attrs={
                'class': 'form-control',
            }),
            'additional_info': forms.Textarea(attrs={
                'class': 'form-control',
            }),
        }


class RoleMealProvision(forms.ModelForm):
    class Meta:
        model = MealProvision
        fields = [
            'role', 'will_provide_meals',
            'meal_charge_amount',
            'additional_info',
        ]
        
        labels = {
            'role': _('roleMealProvisionRole'),
            'will_provide_meals': _('roleMealProvisionWillProvideMeals'),
            'meal_charge_amount': _('roleMealProvisionMealChargeAmount'),
            'additional_info': _('roleMealProvisionAdditionalInfo'),
        }
        
        widgets = {
            'role': forms.Select(attrs={
                'class': 'form-control',
                'readonly': True
            }),
            'will_provide_meals': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'meal_charge_amount': forms.NumberInput(attrs={
                'class': 'form-control',
            }),
            'additional_info': forms.Textarea(attrs={
                'class': 'form-control',
            }),
        }


class TodoFilterForm(forms.Form):
    jobOrder = forms.ModelChoiceField(
        queryset=WorkRequests.objects.exclude(
            status='completed'
        ),
        widget=forms.Select(attrs={'class': 'form-control d-inline w-auto'})
    )
    date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control d-inline w-auto', 'type': 'date'})
    )
    status = forms.ChoiceField(
        choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed')],
        widget=forms.Select(attrs={'class': 'form-control d-inline w-auto'})
    )
    

class OkoMessageFilterForm(forms.Form):
    status = forms.ChoiceField(
        label=_("status"),
        choices=[
            ('inbox', _('inbox')),
            ('sent', _('sent'))   
        ],
        widget=forms.Select(attrs={'class': 'form-control d-inline w-auto'})
    )
    date = forms.DateField(
        label=_("date"), 
        widget=forms.DateInput(attrs={
            'class': 'form-control d-inline w-auto', 'type': 'date'})
    )

class OkoMessageCreateForm(forms.ModelForm):
    class Meta:
        model = OkoMessage
        fields = [
            'recipient_type',
            'job_order',
            'include_recipients',
            'subject',
            'body',
            'auto_reply'
        ]
        
        labels = {
            'recipient_type': _('createMessageRecipientType'),
            'job_order': _('createMessageJobOrder'),
            'include_recipients': _('createMessageIncludeRecipients'),
            'subject': _('createMessageSubject'),
            'body': _('createMessageBody'),
            'auto_reply': _('createMessageAutoReply'),
        }
        
        widgets = {
            'recipient_type': forms.Select(attrs={
                'class': 'form-control',
            }),
            'include_recipients': forms.Select(attrs={
                'class': 'form-control',
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'body': forms.Textarea(attrs={
                'class': 'form-control',
            }),
            'auto_reply': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'job_order': forms.Select(attrs={
                'class': 'form-control',
            }),
        }


class WorkerCreateForm(forms.ModelForm):
    
    gender_choices = [
        ('M', _('male')), 
        ('F', _('female')), 
    ]
    
    gender = forms.ChoiceField(
        choices=gender_choices, 
        widget=forms.Select(attrs={'class': 'form-control'}),
        label=_("gender")
    )
    
    class Meta: 
        model = User
        fields = ['email', 'curp', 'first_name', 'last_name', 'dob', 'gender', 'telephone', 'address_line_1', 'address_line_2', 'city']
        
        labels = {
            'email': _("email"),
            'curp': _("curp"),
            'first_name': _("firstName"),
            'last_name': _("lastName"),
            'dob': _("dateOfBirth"),
            'gender': _("gender"),
            'telephone': _("telephone"),
            'address_line_1': _("addressLine1"),
            'address_line_2': _("addressLine2"),
            'city': _("city"),
        }
        
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'curp': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'dob': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line_1': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line_2': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'})   
        }

class RecruiterAdminCreateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['curp', 'first_name', 'last_name', 'email']

        labels = {
            'curp': _("curp"),
            'first_name': _("firstName"),
            'last_name': _("lastName"),
            'email': _("email"),
            
        }

        widgets = {
            'curp': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            
        }
        

class WorkExperienceCreateForm(forms.ModelForm):
    company = forms.ModelChoiceField(
        queryset=Organization.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label=_("addWorkerExperienceSelectEmployer"),
        label=_("addWorkerExperienceCompany1"),
    )
    class Meta:
        model = UserWorkExperience
        fields = ['user', 'company','work_title', 'start_date', 'end_date', 'country', 'supervisor_name', 'supervisor_tel', 'supervisor_email', 'visa_type']
        
        labels = {
            'user': _("addWorkerExperienceUser"),
            'company': _("addWorkerExperienceCompany"),
            'work_title': _("addWorkerExperienceWorkTitle"),
            'start_date': _("addWorkerExperienceStartDate"),
            'end_date': _("addWorkerExperienceEndDate"),
            'country': _("addWorkerExperienceCountry"),
            'supervisor_name': _("addWorkerExperienceSupervisorName"),
            'supervisor_tel': _("addWorkerExperienceSupervisorTelephone"),
            'supervisor_email': _("addWorkerExperienceSupervisorEmail"),
            'visa_type': _("addWorkerExperienceVisaType"),
        }
    
        widgets = {
            'user': forms.Select(attrs={
                'class': 'form-control', 'readonly': True}),
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'work_title': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'supervisor_name': forms.TextInput(attrs={'class': 'form-control'}),
            'supervisor_tel': forms.TextInput(attrs={'class': 'form-control'}),
            'supervisor_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'visa_type': forms.TextInput(attrs={'class': 'form-control'}),
        }
