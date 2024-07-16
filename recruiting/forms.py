
# create modelform for Employer model
from django import forms
from recruiting.models import Employer

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
        }
