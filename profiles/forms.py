from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from .models import UserProfile
from accounts.models import User


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["avatar", "phone", "address", "bio", "date_of_birth"]
        widgets = {
            "date_of_birth": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "bio": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
        }


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "billing_address",
            "address_complement",
            "country",
        ]
        widgets = {
            "billing_address": forms.Textarea(
                attrs={"rows": 3, "class": "form-control"}
            ),
        }


class ProfessionalUpdateForm(UserUpdateForm):
    class Meta(UserUpdateForm.Meta):
        fields = UserUpdateForm.Meta.fields + [
            "company_name",
            "trading_name",
            "siren",
            "vat_number",
            "legal_form",
            "activity_type",
            "ape_code",
        ]

    def clean_siren(self):
        siren = self.cleaned_data.get("siren")
        if siren and not siren.isdigit():
            raise ValidationError(_("Le SIREN doit contenir uniquement des chiffres."))
        return siren

    def clean_vat_number(self):
        vat = self.cleaned_data.get("vat_number")
        if vat and not vat.startswith("FR"):
            raise ValidationError(_("Le numéro de TVA doit commencer par FR."))
        return vat
