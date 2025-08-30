from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    UserChangeForm,
    AuthenticationForm,
)
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from .models import User, UserProfile, Project


class UserRegistrationForm(UserCreationForm):
    user_type = forms.ChoiceField(
        choices=User.UserType.choices,
        widget=forms.RadioSelect,
        label=_("Type d'utilisateur"),
    )
    civility = forms.ChoiceField(
        choices=User.Civility.choices,
        widget=forms.RadioSelect,
        label=_("Civilité"),
    )
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={"class": "form-control"}),
    )
    account_type = forms.ChoiceField(
        choices=User.AccountType.choices,
        initial=User.AccountType.CLIENT,
        widget=forms.RadioSelect,
        label=_("Type de compte"),
    )

    class Meta:
        model = User
        fields = [
            "email",
            "user_type",
            "civility",
            "first_name",
            "last_name",
            "account_type",
            "password1",
            "password2",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Campos profissionais inicialmente ocultos via JavaScript
        self.professional_fields = [
            "company_name",
            "trading_name",
            "siren",
            "vat_number",
            "legal_form",
            "activity_type",
            "ape_code",
            "billing_address",
        ]

        for field in self.professional_fields:
            self.fields[field] = User._meta.get_field(field).formfield()
            self.fields[field].required = False

    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get("user_type")

        if user_type == User.UserType.PROFESSIONAL:
            required_fields = ["company_name", "siren"]
            for field in required_fields:
                if not cleaned_data.get(field):
                    self.add_error(
                        field,
                        _("Ce champ est obligatoire pour un compte professionnel."),
                    )

        return cleaned_data


class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label=_("Email"), widget=forms.EmailInput(attrs={"class": "form-control"})
    )
    password = forms.CharField(
        label=_("Mot de passe"),
        strip=False,
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )

    error_messages = {
        "invalid_login": _(
            "Veuillez saisir une adresse e-mail et un mot de passe valides. "
            "Notez que les deux champs sont sensibles à la casse."
        ),
        "inactive": _("Ce compte est inactif."),
    }


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


class PasswordResetForm(forms.Form):
    """
    Formulário para solicitar redefinição de senha através do email
    """

    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(
            attrs={
                "class": "w-full px-4 py-2 text-gray-700 bg-white border rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200",
                "placeholder": _("Entrez votre email"),
            }
        ),
    )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not User.objects.filter(email=email, is_active=True).exists():
            raise ValidationError(
                _("Aucun compte actif n'a été trouvé avec cette adresse email.")
            )
        return email
