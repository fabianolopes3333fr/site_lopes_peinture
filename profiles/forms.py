from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import UserProfile
from accounts.models import User
import re


class UserProfileForm(forms.ModelForm):
    """
    Formulário para edição do perfil do usuário.
    Combina informações do User e UserProfile.
    """

    # Campos do User
    first_name = forms.CharField(
        label=_("Prénom"),
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-4 py-2 text-gray-700 bg-white border rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200",
                "placeholder": _("Entrez votre prénom"),
            }
        ),
    )

    last_name = forms.CharField(
        label=_("Nom"),
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "w-full px-4 py-2 text-gray-700 bg-white border rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200",
                "placeholder": _("Entrez votre nom"),
            }
        ),
    )

    class Meta:
        model = UserProfile
        fields = ["avatar", "phone", "address", "bio", "date_of_birth"]
        widgets = {
            "avatar": forms.FileInput(
                attrs={
                    "class": "w-full px-4 py-2 text-gray-700 bg-white border rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200",
                    "accept": "image/*",
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 text-gray-700 bg-white border rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200",
                    "placeholder": _("Ex: +33 6 12 34 56 78"),
                }
            ),
            "address": forms.Textarea(
                attrs={
                    "rows": 3,
                    "class": "w-full px-4 py-2 text-gray-700 bg-white border rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200",
                    "placeholder": _("Entrez votre adresse complète"),
                }
            ),
            "bio": forms.Textarea(
                attrs={
                    "rows": 4,
                    "maxlength": 500,
                    "class": "w-full px-4 py-2 text-gray-700 bg-white border rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200",
                    "placeholder": _("Décrivez-vous en quelques mots..."),
                }
            ),
            "date_of_birth": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "w-full px-4 py-2 text-gray-700 bg-white border rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200",
                }
            ),
        }
        labels = {
            "avatar": _("Photo de profil"),
            "phone": _("Téléphone"),
            "address": _("Adresse"),
            "bio": _("Biographie"),
            "date_of_birth": _("Date de naissance"),
        }
        help_texts = {
            "avatar": _("Formats acceptés: JPG, PNG. Taille max: 2MB"),
            "phone": _("Format international recommandé: +33 6 12 34 56 78"),
            "bio": _("Maximum 500 caractères"),
            "date_of_birth": _("Cette information reste privée"),
        }

    def __init__(self, *args, **kwargs):
        """Initialise le formulaire avec les données du User."""
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if self.user:
            self.fields["first_name"].initial = self.user.first_name
            self.fields["last_name"].initial = self.user.last_name

    def clean_first_name(self):
        """Valida o primeiro nome."""
        first_name = self.cleaned_data.get("first_name")
        if first_name:
            first_name = first_name.strip().title()
            if not re.match(r"^[a-zA-ZÀ-ÿ\s-]+$", first_name):
                raise ValidationError(
                    _("Le prénom ne peut contenir que des lettres, espaces et tirets."),
                    code="invalid_name",
                )
        return first_name

    def clean_last_name(self):
        """Valida o sobrenome."""
        last_name = self.cleaned_data.get("last_name")
        if last_name:
            last_name = last_name.strip().title()
            if not re.match(r"^[a-zA-ZÀ-ÿ\s-]+$", last_name):
                raise ValidationError(
                    _("Le nom ne peut contenir que des lettres, espaces et tirets."),
                    code="invalid_name",
                )
        return last_name

    def clean_date_of_birth(self):
        """Valida a data de nascimento."""
        date_of_birth = self.cleaned_data.get("date_of_birth")
        if date_of_birth:
            today = timezone.now().date()
            if date_of_birth > today:
                raise ValidationError(
                    _("La date de naissance ne peut pas être dans le futur."),
                    code="invalid_date",
                )

            # Verificar idade mínima (13 anos)
            min_age_date = today.replace(year=today.year - 13)
            if date_of_birth > min_age_date:
                raise ValidationError(
                    _("Vous devez avoir au moins 13 ans pour utiliser ce service."),
                    code="min_age",
                )
        return date_of_birth

    def clean_avatar(self):
        """Valida o arquivo de avatar."""
        avatar = self.cleaned_data.get("avatar")
        if avatar:
            # Verificar tamanho do arquivo (2MB)
            if avatar.size > 2 * 1024 * 1024:
                raise ValidationError(
                    _("Le fichier ne peut pas dépasser 2MB."), code="file_too_large"
                )

            # Verificar tipo de arquivo
            allowed_types = ["image/jpeg", "image/png", "image/gif"]
            if avatar.content_type not in allowed_types:
                raise ValidationError(
                    _("Seuls les fichiers JPG, PNG et GIF sont acceptés."),
                    code="invalid_file_type",
                )
        return avatar

    def save(self, commit=True):
        """Salva o perfil e atualiza os dados do User."""
        profile = super().save(commit=False)

        if self.user:
            # Atualizar dados do User
            self.user.first_name = self.cleaned_data.get("first_name", "")
            self.user.last_name = self.cleaned_data.get("last_name", "")

            if commit:
                self.user.save()
                profile.save()
        elif commit:
            profile.save()

        return profile


class AvatarUploadForm(forms.ModelForm):
    """Formulário específico para upload de avatar."""

    class Meta:
        model = UserProfile
        fields = ["avatar"]
        widgets = {
            "avatar": forms.FileInput(
                attrs={"accept": "image/*", "class": "hidden", "id": "avatar-input"}
            )
        }

    def clean_avatar(self):
        """Valida o arquivo de avatar."""
        avatar = self.cleaned_data.get("avatar")
        if avatar:
            # Verificar tamanho do arquivo (2MB)
            if avatar.size > 2 * 1024 * 1024:
                raise ValidationError(_("Le fichier ne peut pas dépasser 2MB."))

            # Verificar tipo de arquivo
            allowed_types = ["image/jpeg", "image/png", "image/gif"]
            if avatar.content_type not in allowed_types:
                raise ValidationError(
                    _("Seuls les fichiers JPG, PNG et GIF sont acceptés.")
                )
        return avatar


# Formulário para atualização básica do User (se necessário)
class UserUpdateForm(forms.ModelForm):
    """Formulário para atualização dos dados básicos do usuário."""

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
        ]  # Apenas campos que existem no modelo User
        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 text-gray-700 bg-white border rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200",
                    "placeholder": _("Prénom"),
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 text-gray-700 bg-white border rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200",
                    "placeholder": _("Nom de famille"),
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "w-full px-4 py-2 text-gray-700 bg-white border rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200",
                    "placeholder": _("Email"),
                    "readonly": True,  # Email geralmente não deve ser editável
                }
            ),
        }
        labels = {
            "first_name": _("Prénom"),
            "last_name": _("Nom"),
            "email": _("Adresse email"),
        }

    def clean_email(self):
        """Impede alteração do email."""
        email = self.cleaned_data.get("email")
        if self.instance and self.instance.email != email:
            raise ValidationError(_("L'adresse email ne peut pas être modifiée."))
        return email

    def clean_first_name(self):
        """Valida o primeiro nome."""
        first_name = self.cleaned_data.get("first_name")
        if first_name:
            first_name = first_name.strip().title()
            if not re.match(r"^[a-zA-ZÀ-ÿ\s-]+$", first_name):
                raise ValidationError(
                    _("Le prénom ne peut contenir que des lettres, espaces et tirets.")
                )
        return first_name

    def clean_last_name(self):
        """Valida o sobrenome."""
        last_name = self.cleaned_data.get("last_name")
        if last_name:
            last_name = last_name.strip().title()
            if not re.match(r"^[a-zA-ZÀ-ÿ\s-]+$", last_name):
                raise ValidationError(
                    _("Le nom ne peut contenir que des lettres, espaces et tirets.")
                )
        return last_name
