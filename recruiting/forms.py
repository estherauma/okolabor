
# create modelform for Employer model
from django import forms
from recruiting.models import (
    Deduction, Employer, Hours, Qualification,
    EmploymentLocation, HousingInformation, MealProvision,
    Role, Wages, WorkRequests
)


class EmployerForm(forms.ModelForm):
    class Meta:
        model = Employer
        fields = ['name', 'email', 'phone', 'website',
                  'address', 'city', 'state', 'country',
                  'zip_code', 'description'
                  ]

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'email': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'website': forms.TextInput(attrs={
                'class': 'form-control',
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
            'country': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'zip_code': forms.TextInput(attrs={
                'class': 'form-control',
            }),
        }


class WorkRequestForm(forms.ModelForm):
    class Meta:
        model = WorkRequests
        fields = [
            'name', 'start_date', 'end_date',
            'required_workers', 'employer', 'status'
        ]

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'requiired_workers': forms.NumberInput(attrs={
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
        self.fields['work_request'].widget.attrs['readonly'] = True
        self.fields['work_request'].required = False  # Prevent validation error

    def clean(self):
        cleaned_data = super().clean()
        # Reassign work_request field value here
        cleaned_data['work_request'] = self.initial.get('work_request')
        return cleaned_data


class WorkRequestRoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = [
            'title', 'usdol_case_number',
            'number_of_required_workers', 'work_request'
        ]

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'usdol_case_number': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'number_of_required_workers': forms.NumberInput(attrs={
                'class': 'form-control',
            }),
            'work_request': forms.Select(attrs={
                'class': 'form-control',
                'readonly': True
            }),
        }


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
        widgets = {
            'on_call': forms.CheckboxInput(attrs={
                'class': 'form-control',
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
            'frequency_of_pay', 'frequency_of_pay_other', 'start_timing'
        ]

        widgets = {
            'wage': forms.NumberInput(attrs={
                'class': 'form-control',
            }),
            'wage_type': forms.Select(attrs={
                'class': 'form-control',
            }),
            'piece_rate_offerings': forms.NumberInput(attrs={
                'class': 'form-control',
            }),
            'frequency_of_pay': forms.Select(attrs={
                'class': 'form-control',
            }),
            'frequency_of_pay_other': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'start_timing': forms.TextInput(attrs={
                'class': 'form-control',
            }),
        }


class RoleDeductionForm(forms.ModelForm):
    class Meta:
        model = Deduction
        fields = ['description', 'deduction_amount']

        widgets = {
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

        widgets = {
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
                'class': 'form-control',
            }),
            'drug_screen': forms.CheckboxInput(attrs={
                'class': 'form-control',
            }),
            'lifting_requirements': forms.TextInput(attrs={
                'class': 'form-control',
            }),
            'lifting_requirement_weight': forms.NumberInput(attrs={
                'class': 'form-control',
            }),
            'exposure_to_temperature': forms.CheckboxInput(attrs={
                'class': 'form-control',
            }),
            'extensive_pushing_or_pulling': forms.CheckboxInput(attrs={
                'class': 'form-control',
            }),
            'extensive_sitting_or_walking': forms.CheckboxInput(attrs={
                'class': 'form-control',
            }),
            'frequent_stooping_or_bending_over': forms.CheckboxInput(attrs={
                'class': 'form-control',
            }),
            'repetitive_movements': forms.CheckboxInput(attrs={
                'class': 'form-control',
            }),
            'support_of_other_employees': forms.CheckboxInput(attrs={
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
            'address', 'city', 'county', 'state',
            'postal_code', 'additional_info'
        ]
        widgets = {
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
            'address', 'city', 'county', 'state',
            'postal_code', 'type_of_housing', 'additional_info'
        ]
        widgets = {
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
            'will_provide_meals', 'meal_charge_amount',
            'additional_info'
        ]
        widgets = {
            'will_provide_meals': forms.CheckboxInput(attrs={
                'class': 'form-control',
            }),
            'meal_charge_amount': forms.NumberInput(attrs={
                'class': 'form-control',
            }),
            'additional_info': forms.Textarea(attrs={
                'class': 'form-control',
            }),
        }
