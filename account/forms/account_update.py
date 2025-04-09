from django import forms
from account.models import User, LanguageChoices
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Group  


class UpdateAccountDetailsForm(forms.ModelForm):
    STATUS_CHOICES = [
        (True, _("Active")),
        (False, _("Inactive")),
    ]

    is_active = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    group = forms.ChoiceField(
        choices=[
            ("recruiter", "Recruiter"),
            ("recruiter_admin", "Recruiter Admin"),
            ("employer", "Employer"),
            ("employer_admin", "Employer Admin")
        ],
        required=True,
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

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

        self.fields["curp"].widget.attrs["readonly"] = True
        self.fields["email"].widget.attrs["readonly"] = True
        self.fields["language"].choices = LanguageChoices.choices
        self.fields["is_active"].initial = str(self.instance.is_active)

        # Initialize group field from user groups
        if self.instance and self.instance.groups.exists():
            self.fields["group"].initial = self.instance.groups.first().name
