from django import forms
from account.models import User
from django.utils.translation import gettext_lazy as _ 

class UpdateAccountDetailsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["curp", "first_name", "last_name", "email"]  
        labels = {
            "curp": _("curp"),  
            "first_name": _("firstName"),
            "last_name": _("lastName"),
            "email": _("email"),
        }

    def __init__(self, *args, **kwargs):
        super(UpdateAccountDetailsForm, self).__init__(*args, **kwargs)
        self.fields["curp"].widget.attrs["readonly"] = True
        self.fields["email"].widget.attrs["readonly"] = True
