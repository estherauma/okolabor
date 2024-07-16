
# create modelform for Employer model
from django import forms
from recruiting.models import Employer, WorkRequests

class EmployerForm(forms.ModelForm):
    
    class Meta:
        model = Employer
        fields = ['name', 'email', 'phone', 'website', 'address', 'city', 'state', 'country', 'zip_code', 'description']

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
        fields = ['name', 'start_date', 'end_date', 'requiired_workers', 'employer', 'status']

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
