from django import forms
from account.models import User

class UpdateAccountDetailsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["curp", "first_name", "last_name", "email"]  

    def __init__(self, *args, **kwargs):
        super(UpdateAccountDetailsForm, self).__init__(*args, **kwargs)
        self.fields["curp"].widget.attrs["readonly"] = True
        self.fields["email"].widget.attrs["readonly"] = True
