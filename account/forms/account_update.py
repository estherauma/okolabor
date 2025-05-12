from django import forms
from account.models import User, LanguageChoices
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Group  


class UpdateAccountDetailsForm(forms.ModelForm):
    STATUS_CHOICES = [
        (True, _("accountActive")),
        (False, _("accountInactive")),
    ]

    is_active = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_("accountStatus"),
    )

    group = forms.ChoiceField(
        choices=[
            ("recruiter", _("accountRecruiter")),
            ("recruiter_admin", _("accountRecruiterAdmin")),
            ("employer", _("accountEmployer")),
            ("employer_admin", _("accountEmployerAdmin"))
        ],
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_("accountGroup"),
    )


    class Meta:
        model = User
        fields = ["curp", "first_name", "last_name", "email", "language", "is_active"]
        labels = {
            "curp": _("accountCURP"),
            "first_name": _("accountFirstName"),
            "last_name": _("accountLastName"),
            "email": _("accountEmail"),
            "language": _("accountLanguage"),
            "is_active": _("accountStatus"),
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
