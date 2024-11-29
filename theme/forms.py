from django import forms
from account.models import UserWorkExperience, UserJobExperience,UserJobExperienceDetails


class RegistrationForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'input100',
            'placeholder': 'Username'
        })
    )
    email = forms.EmailField(
        max_length=150,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'input100',
            'placeholder': 'Email'
        })
    )
    password = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'input100',
            'placeholder': 'Password'
        })
    )


class ResetPasswordForm(forms.Form):
    email = forms.EmailField(
        label='Email',
        max_length=100,
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 
        'placeholder': 'Enter Your Email'})
    )
class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    
    
class FilterWorkExperienceForm(forms.Form):
    work_experience = forms.ModelChoiceField(
        queryset=UserWorkExperience.objects.all(), 
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control d-inline w-auto'
        })
    )
    crop_type = forms.ModelChoiceField(
        queryset=UserJobExperience.objects.values_list('job_type', flat=True).distinct(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control d-inline w-auto',
            'placeholder': 'Crop Type'
        })
    )
    experience_type = forms.ChoiceField(
        choices=UserJobExperienceDetails.KIND_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control d-inline w-auto',
            'placeholder': 'Experience Type'
        })
    )
    
    
    minimum_experience = forms.ChoiceField(
        choices=[
            ('0', 'No Experience'),
            ('1', '1 Year'),
            ('2', '2 Years'),
            ('3', '3 Years'),
            ('5', '5+ Years'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control d-inline w-auto'
        })
    )
    