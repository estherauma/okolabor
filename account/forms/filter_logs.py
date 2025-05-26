from django import forms
from account.models import *
from django.utils.translation import gettext_lazy as _

class UserLogsFilterForm(forms.Form):
    
    date_filter_type = forms.ChoiceField(
        choices=[
            ('today', _('userLogsToday')),
            ('last_7_days', _('userLogsLast7Days')),
            ('this_month', _('userLogsThisMonth'))
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control d-inline w-auto'}),
        label=_("userLogsFilterByDate")
    )
    

    