
# create modelform for Employer model
from django import forms
from account.models import User
from recruiting.models import (
    Deduction, Employer, Hours, OkoMessage, Qualification,
    EmploymentLocation, HousingInformation, MealProvision,
    Role, Wages, WorkRequests
)

from account.models import (UserWorkExperience)

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


class WorkRequestRoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = [
            'title', 'usdol_case_number', 'work_type',
            'number_of_required_workers', 'work_request', 'description'
        ]

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
        choices=[('inbox', 'InBox'), ('sent', 'Sent')],
        widget=forms.Select(attrs={'class': 'form-control d-inline w-auto'})
    )
    date = forms.DateField(
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
        ('M', 'Male'),
        ('F', 'Female'),
        
    ]
    
    gender = forms.ChoiceField(
    choices=gender_choices , 
    widget=forms.Select(attrs={'class': 'form-control'})
)
    class Meta: 
        model = User
        fields = ['email', 'curp', 'first_name', 'last_name', 'dob', 'gender', 'telephone', 'address_line_1', 'address_line_2', 'city']
        
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
        

class WorkExperienceCreateForm(forms.ModelForm):
    company = forms.ModelChoiceField(
        queryset=Employer.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Select Employer",
    )
    class Meta:
        model = UserWorkExperience
        fields = ['user', 'company','work_title', 'start_date', 'end_date', 'country', 'supervisor_name', 'supervisor_tel', 'supervisor_email', 'visa_type']
    
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
