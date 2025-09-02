from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    UserChangeForm,
    AuthenticationForm,
)
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from accounts.models import User
from projects.models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            "type_projet",
            "description",
            "surface",
            "date_debut_souhaitee",
            "date_fin_souhaitee",
            "urgence",
            "adresse_travaux",
            "complement_adresse",
            "code_postal",
            "ville",
            "pays",
            "budget_estime",
        ]
        widgets = {
            "type_projet": forms.Select(attrs={"class": "form-control"}),
            "description": forms.Textarea(
                attrs={
                    "rows": 4,
                    "class": "form-control",
                    "placeholder": _("Décrivez votre projet en détail..."),
                }
            ),
            "surface": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": _("m²")}
            ),
            "date_debut_souhaitee": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "date_fin_souhaitee": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "urgence": forms.Select(attrs={"class": "form-control"}),
            "adresse_travaux": forms.TextInput(
                attrs={"class": "form-control", "placeholder": _("Adresse du chantier")}
            ),
            "complement_adresse": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("Appartement, étage, etc."),
                }
            ),
            "code_postal": forms.TextInput(
                attrs={"class": "form-control", "placeholder": _("Code postal")}
            ),
            "ville": forms.TextInput(
                attrs={"class": "form-control", "placeholder": _("Ville")}
            ),
            "pays": forms.TextInput(
                attrs={"class": "form-control", "initial": "France"}
            ),
            "budget_estime": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": _("€")}
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        date_debut = cleaned_data.get("date_debut_souhaitee")
        date_fin = cleaned_data.get("date_fin_souhaitee")

        if date_debut and date_fin and date_fin < date_debut:
            raise ValidationError(
                {
                    "date_fin_souhaitee": _(
                        "La date de fin ne peut pas être antérieure à la date de début."
                    )
                }
            )

        return cleaned_data
