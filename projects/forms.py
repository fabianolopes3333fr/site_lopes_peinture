from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Project
import re


class ProjectForm(forms.ModelForm):
    """
    Formulário principal para criação e edição de projetos.
    Implementa validações robustas e interface responsiva.
    """

    class Meta:
        model = Project
        fields = [
            "title",
            "type_projet",
            "description",
            "surface",
            "nombre_pieces",
            "date_debut_souhaitee",
            "date_fin_souhaitee",
            "priority",
            "adresse_travaux",
            "complement_adresse",
            "code_postal",
            "ville",
            "pays",
            "budget_estime",
            "notes_client",
        ]

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 text-gray-700 bg-white border rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200",
                    "placeholder": _("Titre descriptif du projet"),
                }
            ),
            "type_projet": forms.Select(
                attrs={
                    "class": "w-full px-4 py-2 text-gray-700 bg-white border rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "rows": 4,
                    "class": "w-full px-4 py-2 text-gray-700 bg-white border rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200",
                    "placeholder": _("Décrivez votre projet en détail..."),
                }
            ),
            "surface": forms.NumberInput(
                attrs={
                    "class": "w-full px-4 py-2 text-gray-700 bg-white border rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200",
                    "placeholder": _("Surface en m²"),
                    "step": "0.01",
                    "min": "0",
                }
            ),
            "nombre_pieces": forms.NumberInput(
                attrs={
                    "class": "w-full px-4 py-2 text-gray-700 bg-white border rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200",
                    "placeholder": _("Nombre de pièces"),
                    "min": "1",
                }
            ),
            "date_debut_souhaitee": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "w-full px-4 py-2 text-gray-700 bg-white border rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200",
                }
            ),
            "date_fin_souhaitee": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "w-full px-4 py-2 text-gray-700 bg-white border rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200",
                }
            ),
            "priority": forms.Select(
                attrs={
                    "class": "w-full px-4 py-2 text-gray-700 bg-white border rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
                }
            ),
            "adresse_travaux": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 text-gray-700 bg-white border rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200",
                    "placeholder": _("Adresse complète du chantier"),
                }
            ),
            "complement_adresse": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 text-gray-700 bg-white border rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200",
                    "placeholder": _("Appartement, étage, bâtiment..."),
                }
            ),
            "code_postal": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 text-gray-700 bg-white border rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200",
                    "placeholder": _("Code postal"),
                    "pattern": "[0-9]{5}",
                }
            ),
            "ville": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 text-gray-700 bg-white border rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200",
                    "placeholder": _("Ville"),
                }
            ),
            "pays": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 text-gray-700 bg-white border rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200",
                    "placeholder": _("Pays"),
                }
            ),
            "budget_estime": forms.NumberInput(
                attrs={
                    "class": "w-full px-4 py-2 text-gray-700 bg-white border rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200",
                    "placeholder": _("Budget approximatif en €"),
                    "step": "0.01",
                    "min": "0",
                }
            ),
            "notes_client": forms.Textarea(
                attrs={
                    "rows": 3,
                    "class": "w-full px-4 py-2 text-gray-700 bg-white border rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200",
                    "placeholder": _("Notes et remarques supplémentaires..."),
                }
            ),
        }

        labels = {
            "title": _("Titre du projet"),
            "type_projet": _("Type de projet"),
            "description": _("Description détaillée"),
            "surface": _("Surface (m²)"),
            "nombre_pieces": _("Nombre de pièces"),
            "date_debut_souhaitee": _("Date de début souhaitée"),
            "date_fin_souhaitee": _("Date de fin souhaitée"),
            "priority": _("Priorité"),
            "adresse_travaux": _("Adresse des travaux"),
            "complement_adresse": _("Complément d'adresse"),
            "code_postal": _("Code postal"),
            "ville": _("Ville"),
            "pays": _("Pays"),
            "budget_estime": _("Budget estimé (€)"),
            "notes_client": _("Notes et remarques"),
        }

    def __init__(self, *args, **kwargs):
        """Inicializa o formulário com configurações personalizadas."""
        super().__init__(*args, **kwargs)

        # Tornar campos obrigatórios
        required_fields = [
            "title",
            "type_projet",
            "description",
            "adresse_travaux",
            "code_postal",
            "ville",
        ]
        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].required = True

        # Configurar data mínima (hoje)
        today = timezone.now().date().isoformat()
        self.fields["date_debut_souhaitee"].widget.attrs["min"] = today
        self.fields["date_fin_souhaitee"].widget.attrs["min"] = today

    def clean_title(self):
        """Valida o título do projeto."""
        title = self.cleaned_data.get("title")
        if title:
            title = title.strip().title()
            if len(title) < 5:
                raise ValidationError(
                    _("Le titre doit contenir au moins 5 caractères."),
                    code="title_too_short",
                )
        return title

    def clean_description(self):
        """Valida a descrição do projeto."""
        description = self.cleaned_data.get("description")
        if description:
            description = description.strip()
            if len(description) < 20:
                raise ValidationError(
                    _("La description doit contenir au moins 20 caractères."),
                    code="description_too_short",
                )
        return description

    def clean_code_postal(self):
        """Valida o código postal francês."""
        code_postal = self.cleaned_data.get("code_postal")
        if code_postal:
            code_postal = code_postal.strip()
            # Validação para código postal francês
            if not re.match(r"^[0-9]{5}$", code_postal):
                raise ValidationError(
                    _("Le code postal doit contenir exactement 5 chiffres."),
                    code="invalid_postal_code",
                )
        return code_postal

    def clean_ville(self):
        """Valida o nome da cidade."""
        ville = self.cleaned_data.get("ville")
        if ville:
            ville = ville.strip().title()
            if not re.match(r"^[a-zA-ZÀ-ÿ\s\-\']+$", ville):
                raise ValidationError(
                    _(
                        "Le nom de la ville ne peut contenir que des lettres, espaces, tirets et apostrophes."
                    ),
                    code="invalid_city_name",
                )
        return ville

    def clean_surface(self):
        """Valida a superfície."""
        surface = self.cleaned_data.get("surface")
        if surface is not None:
            if surface <= 0:
                raise ValidationError(
                    _("La surface doit être positive."), code="invalid_surface"
                )
            if surface > 10000:  # Limite razoável
                raise ValidationError(
                    _("La surface semble trop importante. Veuillez vérifier."),
                    code="surface_too_large",
                )
        return surface

    def clean_budget_estime(self):
        """Valida o orçamento estimado."""
        budget = self.cleaned_data.get("budget_estime")
        if budget is not None:
            if budget <= 0:
                raise ValidationError(
                    _("Le budget doit être positif."), code="invalid_budget"
                )
            if budget > 1000000:  # Limite razoável
                raise ValidationError(
                    _("Le budget semble très élevé. Veuillez vérifier."),
                    code="budget_too_high",
                )
        return budget

    def clean_date_debut_souhaitee(self):
        """Valida a data de início desejada."""
        date_debut = self.cleaned_data.get("date_debut_souhaitee")
        if date_debut:
            # Verificar se não é muito no passado (mais de 30 dias)
            limite_passado = timezone.now().date() - timezone.timedelta(days=30)
            if date_debut < limite_passado:
                raise ValidationError(
                    _("La date de début ne peut pas être trop ancienne."),
                    code="date_too_old",
                )

            # Verificar se não é muito no futuro (mais de 2 anos)
            limite_futuro = timezone.now().date() + timezone.timedelta(days=730)
            if date_debut > limite_futuro:
                raise ValidationError(
                    _("La date de début ne peut pas être si éloignée dans le futur."),
                    code="date_too_future",
                )
        return date_debut

    def clean(self):
        """Validações que dependem de múltiplos campos."""
        cleaned_data = super().clean()

        date_debut = cleaned_data.get("date_debut_souhaitee")
        date_fin = cleaned_data.get("date_fin_souhaitee")

        # Validar relação entre datas
        if date_debut and date_fin:
            if date_fin <= date_debut:
                raise ValidationError(
                    {
                        "date_fin_souhaitee": _(
                            "La date de fin doit être postérieure à la date de début."
                        )
                    }
                )

            # Verificar se o prazo não é muito longo (mais de 1 ano)
            if (date_fin - date_debut).days > 365:
                raise ValidationError(
                    {
                        "date_fin_souhaitee": _(
                            "La durée du projet semble très longue. Veuillez vérifier."
                        )
                    }
                )

        return cleaned_data


class ProjectStatusForm(forms.ModelForm):
    """Formulário para atualização de status do projeto (para staff)."""

    class Meta:
        model = Project
        fields = ["status", "notes_internes", "devis_montant"]
        widgets = {
            "status": forms.Select(
                attrs={
                    "class": "w-full px-4 py-2 text-gray-700 bg-white border rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
                }
            ),
            "notes_internes": forms.Textarea(
                attrs={
                    "rows": 4,
                    "class": "w-full px-4 py-2 text-gray-700 bg-white border rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200",
                    "placeholder": _("Notes internes pour l'équipe..."),
                }
            ),
            "devis_montant": forms.NumberInput(
                attrs={
                    "class": "w-full px-4 py-2 text-gray-700 bg-white border rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200",
                    "step": "0.01",
                    "min": "0",
                }
            ),
        }


class ProjectFilterForm(forms.Form):
    """Formulário para filtrar projetos."""

    STATUS_CHOICES = [("", _("Tous les statuts"))] + Project.Status.choices
    TYPE_CHOICES = [("", _("Tous les types"))] + Project.ProjectType.choices
    PRIORITY_CHOICES = [("", _("Toutes les priorités"))] + Project.Priority.choices

    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={"class": "px-4 py-2 border rounded-lg focus:border-blue-500"}
        ),
    )

    type_projet = forms.ChoiceField(
        choices=TYPE_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={"class": "px-4 py-2 border rounded-lg focus:border-blue-500"}
        ),
    )

    priority = forms.ChoiceField(
        choices=PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(
            attrs={"class": "px-4 py-2 border rounded-lg focus:border-blue-500"}
        ),
    )

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "px-4 py-2 border rounded-lg focus:border-blue-500",
                "placeholder": _("Rechercher par titre, ville, description..."),
            }
        ),
    )
