from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    UserChangeForm,
    AuthenticationForm,
)
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from .models import User


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
