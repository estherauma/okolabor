from django import forms
from account.models import *

class UserLogsFilterForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control d-inline w-auto'})
    )
    
    date_filter_type = forms.ChoiceField(
        choices=[('today', 'Today'), ('last_7_days', 'Last 7 Days'), ('this_month', 'This Month')],
        
        widget=forms.Select(attrs={'class': 'form-control d-inline w-auto'})
    )

    