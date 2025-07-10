
# create modelform for Employer model
from django import forms
from django.utils.translation import gettext_lazy as _ 
from account.models import User
from recruiting.models import (
    Deduction, Organization, Hours, OkoMessage, Qualification,
    EmploymentLocation, HousingInformation, MealProvision,
    Role, Wages, WorkRequests,WorkAssignment
)
from django.core.exceptions import ValidationError
from account.models import (UserWorkExperience)
from common.utils import StaticContent
import os
import json
from django.utils.translation import get_language
from django.conf import settings

class EmployerForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = [
            'name', 'email', 'phone', 'website',
            'address', 'city', 'state', 'country',
            'zip_code', 'description'
        ]

        labels = {
            'name': _('addEmployerName'),
            'email': _('addEmployerEmail'),
            'phone': _('addEmployerTelephone'),
            'website': _('addEmployerWebsite'),
            'address': _('addEmployerAddress'),
            'city': _('addEmployerCity'),
            'state': _('addEmployerState'),
            'country': _('addEmployerCountry'),
            'zip_code': _('addEmployerZipCode'),
            'description': _('addEmployerDescription'),
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
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].required = False



class WorkRequestForm(forms.ModelForm):
    class Meta:
        model = WorkRequests
        fields = [
            'name', 'start_date', 'end_date',
            'required_workers', 'employer', 'status'
        ]
        
        labels = {
            'name': _("createJobOrderName"),
            'start_date': _("createJobOrderStartDate"),
            'end_date': _("createJobOrderEndDate"),
            'required_workers': _("createJobOrderRequiredWorkers"),
            'employer': _("createJobOrderEmployer"),
            'status': _("createJobOrderStatus"),
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
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employer'].queryset = Organization.objects.filter(type='employer').order_by('name')

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


from django import forms
from django.forms import CheckboxSelectMultiple
from .models import Role

class WorkRequestRoleForm(forms.ModelForm):
    work_type = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_type_sector'}),
        required=True,
    )

    # Optional dynamic fields using checkboxes now
    animal_types = forms.MultipleChoiceField(
        required=False,
        widget=CheckboxSelectMultiple(attrs={'class': 'form-check-input', 'id': 'id_animal_types'}),
    )
    crop_types = forms.MultipleChoiceField(
        required=False,
        widget=CheckboxSelectMultiple(attrs={'class': 'form-check-input', 'id': 'id_crop_types'}),
    )
    crop_job_types = forms.MultipleChoiceField(
        required=False,
        widget=CheckboxSelectMultiple(attrs={'class': 'form-check-input', 'id': 'id_crop_job_types'}),
    )
    mechanic_job_types = forms.MultipleChoiceField(
        required=False,
        widget=CheckboxSelectMultiple(attrs={'class': 'form-check-input', 'id': 'id_mechanic_job_types'}),
    )
    supervision_jobs_types = forms.MultipleChoiceField(
        required=False,
        widget=CheckboxSelectMultiple(attrs={'class': 'form-check-input', 'id': 'id_supervision_jobs_types'}),
    )
    licensed_vehicle_operation_types = forms.MultipleChoiceField(
        required=False,
        widget=CheckboxSelectMultiple(attrs={'class': 'form-check-input', 'id': 'licensed_vehicle_operation_types'}),
    )
    responsibilities_types = forms.MultipleChoiceField(
        required=False,
        widget=CheckboxSelectMultiple(attrs={'class': 'form-check-input', 'id': 'id_responsibilities_types'}),
    )

    class Meta:
        model = Role
        fields = [
            'title',
            'usdol_case_number',
            'work_type',
            'animal_types',
            'crop_types',
            'crop_job_types',
            'mechanic_job_types',
            'supervision_jobs_types',
            'responsibilities_types',
            'number_of_required_workers',
            'licensed_vehicle_operation_types',
            'work_request',
            'description',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'usdol_case_number': forms.TextInput(attrs={'class': 'form-control'}),
            'number_of_required_workers': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'work_request': forms.Select(attrs={'class': 'form-control', 'readonly': True}),
        }
        
        labels = {
            'title': _('addRoleTitle'),
            'usdol_case_number': _('addRoleUsdolCaseNumber'),
            'work_type': _('addRoleWorkType'),
            'animal_types': _('addRoleAnimalTypes'),
            'crop_types': _('addRoleCropTypes'),
            'crop_job_types': _('addRoleCropJobTypes'),
            'mechanic_job_types': _('addRoleMechanicJobTypes'),
            'supervision_jobs_types': _('addRoleSupervisionJobsTypes'),
            'responsibilities_types': _('addRoleResponsibilitiesTypes'),
            'number_of_required_workers': _('addRoleNumberOfRequiredWorkers'),
            'licensed_vehicle_operation_types': _('addRoleLicensedVehicleOperationTypes'),
            'work_request': _('addRoleWorkRequest'),
            'description': _('addRoleDescription'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        content_service = StaticContent()

        self.fields['work_type'].choices = content_service.get_sector_choices()

        field_config = {
            'animal_types': {
                'choices': content_service.get_animal_type_choices,
                'label': content_service.get_label_for_field('animalType'),
            },
            'responsibilities_types': {
                'choices': content_service.get_animal_responsibilities_choices,
                'label': content_service.get_label_for_field('responsibilities'),
            },
            'crop_types': {
                'choices': content_service.get_crop_type_choices,
                'label': content_service.get_label_for_field('cropType'),
            },
            'crop_job_types': {
                'choices': content_service.get_crop_responsibilities_choices,
                'label': content_service.get_label_for_field('crop_job_types'),
            },
            'mechanic_job_types': {
                'choices': content_service.get_mechanics_responsibilities_choices,
                'label': content_service.get_label_for_field('mechanic_job_types'),
            },
            'supervision_jobs_types': {
                'choices': content_service.get_worker_supervision_choices,
                'label': content_service.get_label_for_field('supervision_jobs_types'),
            },
            'licensed_vehicle_operation_types': {
                'choices': content_service.get_worker_licensed_vehicle_operation_choices,
                'label': content_service.get_label_for_field('licensed_vehicle_operation_types'),
            },
        }

        for field_name, config in field_config.items():
            if field_name in self.fields:
                self.fields[field_name].choices = config['choices']()
                self.fields[field_name].label = config['label']
                
        self.fields['work_request'].queryset = WorkRequests.objects.order_by('name')

    def clean(self):
        cleaned_data = super().clean()
        work_type = cleaned_data.get("work_type", "").strip().lower()
        request = self.data
        work_type_detail = {}

        def strip_list(field_name):
            return [item.strip() for item in request.getlist(field_name) if item.strip()]

        dynamic_fields_by_type = {
            "animals": ["animal_types", "responsibilities_types"],
            "crop_and_horticulture": ["crop_types", "crop_job_types"],
            "mechanics": ["mechanic_job_types"],
            "worker_supervision__management": ["supervision_jobs_types"],
            "licensed_vehicle_operation": ["licensed_vehicle_operation_types"],
        }

        if work_type in dynamic_fields_by_type:
            for field in dynamic_fields_by_type[work_type]:
                work_type_detail[field] = strip_list(field)

        cleaned_data["work_type"] = work_type
        cleaned_data["work_type_detail"] = work_type_detail
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.work_type_detail = self.cleaned_data.get("work_type_detail", {})
        if commit:
            instance.save()
        return instance


class RoleHoursForm(forms.ModelForm):
    class Meta:
        model = Hours
        fields = [
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
        exclude = ['role']
        
        labels = {
            'role': _('roleHoursRole'),
            'on_call': _('roleHoursOnCall'),
            'estimate_weekly_hours': _('roleHoursEstimatedWeeklyHours'),
            'sunday_hours': _('roleHoursSundayHours'),
            'monday_hours': _('roleHoursMondayHours'),
            'tuesday_hours': _('roleHoursTuesdayHours'),
            'wednesday_hours': _('roleHoursWednesdayHours'),
            'thursday_hours': _('roleHoursThursdayHours'),
            'friday_hours': _('roleHoursFridayHours'),
            'saturday_hours': _('roleHoursSaturdayHours'),
            'job_description': _('roleHoursJobDescription'),
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
            'wage', 'wage_type', 'piece_rate_offerings',
            'piece_rate_offerings_type', 'frequency_of_pay',
            'details'
        ]
        exclude = ['role']
        
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
                'placeholder': '$'
            }),
            'wage_type': forms.Select(attrs={
                'class': 'form-control',
            }),
            'piece_rate_offerings': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '$'
            }),
            'piece_rate_offerings_type': forms.Select(attrs={
                'class': 'form-control',
            }),
            'frequency_of_pay': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'select frequency'
            }),
            'details': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'start typing'
            }),
        }
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            # Required fields
            self.fields['role'].required = True
            self.fields['wage'].required = True
            self.fields['wage_type'].required = True
            self.fields['frequency_of_pay'].required = True

            # Optional fields
            self.fields['details'].required = False
            self.fields['piece_rate_offerings'].required = False
            self.fields['piece_rate_offerings_type'].required = False


class RoleDeductionForm(forms.ModelForm):
    class Meta:
        model = Deduction
        fields = ['description', 'deduction_amount','frequency_of_pay']
        exclude = ['role']
        
        labels = {
            'role': _('roleDeductionsRole'),
            'description': _('roleDeductionsDescription'),
            'deduction_amount': _('roleDeductionsDeductionAmount'),
            'frequency_of_pay': _('roleDeductionsFrequencyOfPay'),
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
            'frequency_of_pay': forms.Select(attrs={
                'class': 'form-control',
            }),
        }


class RoleQualificationForm(forms.ModelForm):
    YES_NO_CHOICES = [
        (True, _('Yes')),
        (False, _('No')),
    ]

    training_required = forms.ChoiceField(
        choices=YES_NO_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),  # Use RadioSelect here
        label=_('roleQualificationTrainingRequired'),
        required=False
    )
    class Meta:
        model = Qualification
        fields = [
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
        exclude = ['role']
        
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
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Set all fields except 'role' to not required
            for field_name in self.fields:
                if field_name != 'role':
                    self.fields[field_name].required = False


class RoleEmploymentLocationForm(forms.ModelForm):
    class Meta:
        model = EmploymentLocation
        fields = [
            'address', 'city', 'county', 'state',
            'postal_code', 'additional_info', 'role'
        ]
        exclude = ['role']

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Load countries.json
        file_path = os.path.join(settings.BASE_DIR, 'recruiting','countries.json')
        with open(file_path, 'r', encoding='utf-8') as f:
            countries = json.load(f)
        lang = get_language()
        lang_key = 'en'
        if lang.lower() in ['es', 'es-mx']:
            lang_key = 'es-MX'

        # Build choices list
        country_choices = [('', 'SelectCountry')]  # Default empty
        for country in countries:
            if country.get('enabled'):
                label = f"{country.get(lang_key)}"
                value = country.get('code')
                country_choices.append((value, label))

        # Override county field as ChoiceField
        self.fields['county'] = forms.ChoiceField(
            choices=country_choices,
            label=self.fields['county'].label,
            widget=forms.Select(attrs={'class': 'form-control'})
        )


class RoleHousingInformationForm(forms.ModelForm):
    class Meta:
        model = HousingInformation
        fields = [
            'address', 'city', 'county', 'state',
            'postal_code', 'type_of_housing', 'additional_info'
        ]
        exclude = ['role']

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
            'role': forms.Select(attrs={'class': 'form-control', 'readonly': True}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'county': forms.TextInput(attrs={'class': 'form-control'}),  # Temporarily here, will override below
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'type_of_housing': forms.Select(attrs={'class': 'form-control'}),
            'additional_info': forms.Textarea(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Load countries.json
        file_path = os.path.join(settings.BASE_DIR, 'recruiting', 'countries.json')
        with open(file_path, 'r', encoding='utf-8') as f:
            countries = json.load(f)

        # Get current language
        lang = get_language()
        lang_key = 'en'
        if lang.lower() in ['es', 'es-mx']:
            lang_key = 'es-MX'

        # Build country choices
        country_choices = [('', 'SelectCountry')]
        for country in countries:
            if country.get('enabled'):
                label = f"{country.get(lang_key)}"
                value = country.get('code')
                country_choices.append((value, label))

        # Override 'county' field with country dropdown
        self.fields['county'] = forms.ChoiceField(
            choices=country_choices,
            label=self.fields['county'].label,
            widget=forms.Select(attrs={'class': 'form-control'})
        )


class RoleMealProvision(forms.ModelForm):
    class Meta:
        model = MealProvision
        fields = [
            'will_provide_meals',
            'meal_charge_amount',
            'additional_info',
        ]
        exclude = ['role']
        
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
                'placeholder': 'Charge amount per day'
            }),
            'additional_info': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'start typing'
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
        label=_("messagesStatus"),
        choices=[
            ('inbox', _('messagesInbox')),
            ('sent', _('messagesSent'))   
        ],
        widget=forms.Select(attrs={'class': 'form-control d-inline w-auto'})
    )
    date = forms.DateField(
        label=_("messagesDate"), 
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
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['job_order'].queryset = WorkRequests.objects.order_by('name')


class WorkerCreateForm(forms.ModelForm):
    gender_choices = [
        ('M', _('addWorkerMale')),
        ('F', _('addWorkerFemale')),
    ]

    gender = forms.ChoiceField(
        choices=gender_choices,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label=_("addWorkerGender")
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = User
        fields = [
            'email', 'curp', 'first_name', 'last_name', 'dob', 'gender',
            'telephone', 'address_line_1', 'address_line_2', 'city'
            
        ]
        
        labels = {
            'email':_('addWorkerEmail'),
            'curp': _('addWorkerCurp'), 
            'first_name': _('addWorkerFirstName'),
            'last_name': _('addWorkerLastName'), 
            'dob': _('addWorkerDateOfBirth'), 
            'gender': _('addWorkerGender'),
            'telephone': _('addWorkerTelephone'), 
            'address_line_1': _('addWorkerAddressLine1'), 
            'address_line_2': _('addWorkerAddressLine2'), 
            'city': _('addWorkerCity')
        }
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'curp': forms.TextInput(attrs={'class': 'form-control','required': True}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'dob': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line_1': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line_2': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
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
    type_sector = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_type_sector'}),
    )

    animal_types = forms.MultipleChoiceField(
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'id': 'id_animal_types'}),
        required=False,
    )

    responsibilities_types = forms.MultipleChoiceField(
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'id': 'id_animal_jobs'}),
        required=False,
    )

    crop_types = forms.MultipleChoiceField(
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'id': 'id_crop_types'}),
        required=False,
    )

    crop_job_types = forms.MultipleChoiceField(
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'id': 'id_crop_jobs'}),
        required=False,
    )

    company = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )

    mechanic_job_types = forms.MultipleChoiceField(
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'id': 'id_mechanic_jobs'}),
        required=False,
    )

    supervision_jobs_types = forms.MultipleChoiceField(
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'id': 'id_supervision_jobs'}),
        required=False,
    )

    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'id': 'id_description'}),
        required=False,
    )

    visa_file = forms.FileField(required=False)
    certificate_file = forms.FileField(required=False)
    video_file = forms.FileField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        content_service = StaticContent()

        field_config = {
            'type_sector': {
                'choices': content_service.get_sector_choices,
                'label': content_service.get_label_for_field('primaryJobType'),
            },
            'animal_types': {
                'choices': content_service.get_animal_type_choices,
                'label': content_service.get_label_for_field('animalType'),
            },
            'responsibilities_types': {
                'choices': content_service.get_animal_responsibilities_choices,
                'label': content_service.get_label_for_field('responsibilities'),
            },
            'crop_types': {
                'choices': content_service.get_crop_type_choices,
                'label': content_service.get_label_for_field('cropType'),
            },
            'crop_job_types': {
                'choices': content_service.get_crop_responsibilities_choices,
                'label': content_service.get_label_for_field('crop_job_types'),
            },
            'mechanic_job_types': {
                'choices': content_service.get_mechanics_responsibilities_choices,
                'label': content_service.get_label_for_field('mechanic_job_types'),
            },
            'supervision_jobs_types': {
                'choices': content_service.get_worker_supervision_choices,
                'label': content_service.get_label_for_field('supervision_jobs_types'),
            },
            'company': {
                'label': content_service.get_label_for_field('company'),
            },
            'description': {
                'label': content_service.get_label_for_field('explanation'),
            },
            'visa_file': {
                'label': content_service.get_label_for_field('visa'),
            },
            'certificate_file': {
                'label': content_service.get_label_for_field('certificate'),
            },
            'video_file': {
                'label': content_service.get_label_for_field('explanation_video'),
            },
        }

        for field_name, config in field_config.items():
            if field_name in self.fields:
                if 'choices' in config:
                    self.fields[field_name].choices = config['choices']()
                if 'label' in config:
                    self.fields[field_name].label = config['label']

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        if start_date and end_date and start_date > end_date:
            raise ValidationError({
                "end_date": _("endDateCannotBeEarlierThanStartDate.")
            })

    class Meta:
        model = UserWorkExperience
        fields = [
            'user', 'company', 'work_title', 'start_date', 'end_date',
            'country', 'supervisor_name', 'supervisor_tel', 'supervisor_email',
            'visa_type'
        ]
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
                'class': 'form-control',
                'readonly': 'readonly',
                'style': 'pointer-events: none; background-color: #e9ecef;',
            }),
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
