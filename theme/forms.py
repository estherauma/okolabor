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
    
class AdvancedFilterForm(forms.Form):
    choices = [
        ('no_experience', 'No experience'),
        ('1_week', '1 week'),
        ('2_weeks', '2 weeks'),
        ('3_weeks', '3 weeks'),
        ('1_month', '1 month'),
        ('2_months', '2 months'),
        ('3_months', '3 months'),
        ('1_year', '1 year'),
        ('2_years', '2 years'),
        ('3_years', '3 years'),
    ]
    
    experience = forms.ChoiceField(
        choices=choices,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='H2A Experience'
    )

    
    total_experience = forms.ChoiceField(
    choices=[
        ('no_experience', 'No experience'),
        ('1_week', '1 week'),
        ('2_weeks', '2 weeks'),
        ('3_weeks', '3 weeks'),
        ('1_month', '1 month'),
        ('2_months', '2 months'),
        ('3_months', '3 months'),
        ('1_year', '1 year'),
        ('2_years', '2 years'),
        ('3_years', '3 years'),
    ],
    widget=forms.Select(attrs={'class': 'form-control'}),
    label='Total years of experience'
    )

    
    documented_experience = forms.ChoiceField(
    choices=[
        ('yes', 'Yes'),
        ('no', 'No'),
    ],
    widget=forms.Select(attrs={'class': 'form-control'}),
    label='Documented experience'
    )

    english_proficiency = forms.ChoiceField(
    choices=[
        ('fluent', 'Fluent'),
        ('advanced', 'Advanced'),
        ('intermediate', 'Intermediate'),
        ('basic', 'Basic'),
    ],
    widget=forms.Select(attrs={'class': 'form-control'}),
    label='English proficiency'
    )

    availability = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'placeholder': 'Select availability',
            'type': 'date'  
        }),
        label='Availability'
    )
    from_worker_order = forms.ChoiceField(
        choices=[
            ('322543', '322543'),
            ('123456', '123456'),
            ('654321', '654321'),
            ('987654', '987654'),
            ('112233', '112233'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control',
            'placeholder': 'From worker order'
        }),
        label='From worker order'
    )
    location_preference = forms.ChoiceField(
    choices=[
        ('mexico', 'Mexico'),
        ('united_states', 'United States'),
        ('afghanistan', 'Afghanistan'),
        ('albania', 'Albania'),
        ('algeria', 'Algeria'),
        ('american_samoa', 'American Samoa'),
        ('andorra', 'Andorra'),
        ('angola', 'Angola'),
        ('anguilla', 'Anguilla'),
    ],
    widget=forms.Select(attrs={
        'class': 'form-control',
        'placeholder': 'Location preference'
    }),
    label='Location preference'
    )

    requested_employer = forms.ChoiceField(
    choices=[
        ('utah_farms', 'Utah Farms'),
        ('employer_1', 'Employer 1'), 
        ('employer_2', 'Employer 2'),
        ('employer_3', 'Employer 3'),
    ],
    widget=forms.Select(attrs={
        'class': 'form-control',
        'placeholder': 'Requested employer'
    }),
    label='Requested employer'
    )

    driver_license = forms.ChoiceField(
    choices=[
        ('united_states', 'United States'),
        ('mexico', 'Mexico'),
        ('afghanistan', 'Afghanistan'),
        ('albania', 'Albania'),
        ('algeria', 'Algeria'),
        ('american_samoa', 'American Samoa'),
        ('andorra', 'Andorra'),
        ('angola', 'Angola'),
        ('anguilla', 'Anguilla'),
    ],
   
    widget=forms.Select(attrs={
        'class': 'form-control',
        'placeholder': 'Driver license'
    }),
    label='Driver license'
    )

    lifting = forms.ChoiceField(
    choices=[
        ('yes', 'Yes'),
        ('no', 'No'),
    ],
    required=True,
    widget=forms.Select(attrs={
        'class': 'form-control',
        'placeholder': 'Able to lift 27kgs'
    }),
    label='Able to lift 27kgs?'
    )

    time_on_feet = forms.ChoiceField(
    choices=[
        ('yes', 'Yes'),
        ('no', 'No'),
    ],
    
    widget=forms.Select(attrs={
        'class': 'form-control',
        'placeholder': 'Will spend time on feet'
    }),
    label='Will spend time on feet?'
    )

    weather = forms.ChoiceField(
    choices=[
        ('yes', 'Yes'),
        ('no', 'No'),
    ],
    
    widget=forms.Select(attrs={
        'class': 'form-control',
        'placeholder': 'Will work in hot & cold?'
    }),
    label='Will work in hot & cold?'
    )

    offer_status = forms.ChoiceField(
    choices=[
        ('pending', 'Pending'),
    ],
    
    widget=forms.Select(attrs={
        'class': 'form-control',
        'placeholder': 'Offer status'
    }),
    label='Offer status'
    )
    
