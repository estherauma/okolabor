from django import forms

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
