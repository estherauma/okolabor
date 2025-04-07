from django import forms
from account.models import User, LanguageChoices
from django.utils.translation import gettext_lazy as _


class UpdateAccountDetailsForm(forms.ModelForm):
    STATUS_CHOICES = [
        (True, _("Active")),
        (False, _("Inactive")),
    ]

    is_active = forms.ChoiceField(
        choices=STATUS_CHOICES, 
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = User
        fields = ["curp", "first_name", "last_name", "email", "language", "is_active"]
        labels = {
            "curp": _("CURP"),
            "first_name": _("First Name"),
            "last_name": _("Last Name"),
            "email": _("Email"),
            "is_active": _("Status"),
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

        # Ensure the status field reflects the user's current state
        self.fields["is_active"].initial = str(self.instance.is_active)