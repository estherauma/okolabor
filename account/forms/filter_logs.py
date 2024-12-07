from django import forms
from account.models import *

class UserLogsFilterForm(forms.Form):
    
    date_filter_type = forms.ChoiceField(
        choices=[
            ('today', 'Today'),
            ('last_7_days', 'Last 7 Days'),
            ('this_month', 'This Month')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control d-inline w-auto'}),
        label="Filter by date"
    )
    

    