from django import forms
from account.models import User, LanguageChoices
from django.utils.translation import gettext_lazy as _


class UpdateAccountDetailsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["curp", "first_name", "last_name", "email", "language"]
        labels = {
            "curp": _("curp"),
            "first_name": _("firstName"),
            "last_name": _("lastName"),
            "email": _("email"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Apply 'form-control' CSS class to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

        # Make 'curp' and 'email' fields readonly
        self.fields["curp"].widget.attrs["readonly"] = True
        self.fields["email"].widget.attrs["readonly"] = True

        # Override language choices if needed
        self.fields["language"].choices = LanguageChoices.choices
