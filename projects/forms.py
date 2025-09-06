from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.admin.widgets import AdminDateWidget
from decimal import Decimal
import re
import logging

from .models import Project, Devis, DevisLine, Product

logger = logging.getLogger(__name__)


class ProjectForm(forms.ModelForm):
    """
    Formulário completo para criação e edição de projetos.
    """

    class Meta:
        model = Project
        fields = [
            # Informações gerais
            "title",
            "type_projet",
            "description",
            # Détails techniques
            "surface_totale",
            "surface_murs",
            "surface_plafond",
            "hauteur_sous_plafond",
            "nombre_pieces",
            "types_pieces",
            "etat_support",
            "preparation_necessaire",
            "type_finition",
            "couleurs_souhaitees",
            "materiaux_specifiques",
            "acces_difficile",
            "contraintes_horaires",
            # Dates
            "date_debut_souhaitee",
            "date_fin_souhaitee",
            # Adresse
            "adresse_travaux",
            "complement_adresse",
            "code_postal",
            "ville",
            "pays",
            "contact_nom",
            "contact_telephone",
            # Budget
            "budget_minimum",
            "budget_maximum",
            # Priorité
            "priority",
            # Notes
            "notes_client",
        ]

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "Ex: Peinture salon et cuisine",
                    "maxlength": 200,
                }
            ),
            "type_projet": forms.Select(attrs={"class": "form-select"}),
            "description": forms.Textarea(
                attrs={
                    "class": "form-textarea",
                    "rows": 4,
                    "placeholder": "Décrivez votre projet en détail...",
                }
            ),
            "surface_totale": forms.NumberInput(
                attrs={"class": "form-input", "step": "0.01", "min": "0", "placeholder": "0.00"}
            ),
            "surface_murs": forms.NumberInput(
                attrs={"class": "form-input", "step": "0.01", "min": "0", "placeholder": "0.00"}
            ),
            "surface_plafond": forms.NumberInput(
                attrs={"class": "form-input", "step": "0.01", "min": "0", "placeholder": "0.00"}
            ),
            "hauteur_sous_plafond": forms.NumberInput(
                attrs={"class": "form-input", "step": "0.01", "min": "0", "placeholder": "2.50"}
            ),
            "nombre_pieces": forms.NumberInput(
                attrs={"class": "form-input", "min": "1", "placeholder": "1"}
            ),
            "etat_support": forms.Select(attrs={"class": "form-select"}),
            "preparation_necessaire": forms.Textarea(
                attrs={
                    "class": "form-textarea",
                    "rows": 3,
                    "placeholder": "Travaux de préparation nécessaires...",
                }
            ),
            "type_finition": forms.Select(attrs={"class": "form-select"}),
            "materiaux_specifiques": forms.Textarea(
                attrs={
                    "class": "form-textarea",
                    "rows": 3,
                    "placeholder": "Marques ou matériaux spécifiques...",
                }
            ),
            "acces_difficile": forms.CheckboxInput(attrs={"class": "form-checkbox"}),
            "contraintes_horaires": forms.Textarea(
                attrs={
                    "class": "form-textarea",
                    "rows": 3,
                    "placeholder": "Contraintes d'horaires ou de planning...",
                }
            ),
            "date_debut_souhaitee": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "date_fin_souhaitee": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "adresse_travaux": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "Adresse complète des travaux",
                }
            ),
            "complement_adresse": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "Appartement, étage, bâtiment...",
                }
            ),
            "code_postal": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "75001", "maxlength": 10}
            ),
            "ville": forms.TextInput(attrs={"class": "form-input", "placeholder": "Paris"}),
            "pays": forms.TextInput(attrs={"class": "form-input", "value": "France"}),
            "contact_nom": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "Nom du contact sur site",
                }
            ),
            "contact_telephone": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "+33 1 23 45 67 89"}
            ),
            "budget_minimum": forms.NumberInput(
                attrs={"class": "form-input", "step": "0.01", "min": "0", "placeholder": "0.00"}
            ),
            "budget_maximum": forms.NumberInput(
                attrs={"class": "form-input", "step": "0.01", "min": "0", "placeholder": "0.00"}
            ),
            "priority": forms.Select(attrs={"class": "form-select"}),
            "notes_client": forms.Textarea(
                attrs={
                    "class": "form-textarea",
                    "rows": 4,
                    "placeholder": "Remarques et demandes spécifiques...",
                }
            ),
        }

    # ================================
    # CAMPOS CUSTOMIZADOS
    # ================================

    # Campo para tipos de pièces com checkboxes
    pieces_salon = forms.BooleanField(
        label=_("Salon"),
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-checkbox"}),
    )
    pieces_cuisine = forms.BooleanField(
        label=_("Cuisine"),
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-checkbox"}),
    )
    pieces_chambre = forms.BooleanField(
        label=_("Chambre"),
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-checkbox"}),
    )
    pieces_salle_de_bain = forms.BooleanField(
        label=_("Salle de bain"),
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-checkbox"}),
    )
    pieces_bureau = forms.BooleanField(
        label=_("Bureau"),
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-checkbox"}),
    )
    pieces_couloir = forms.BooleanField(
        label=_("Couloir"),
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-checkbox"}),
    )
    pieces_exterieur = forms.BooleanField(
        label=_("Extérieur"),
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-checkbox"}),
    )

    # Campos para couleurs
    couleur_murs = forms.CharField(
        label=_("Couleur des murs"),
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-input", "placeholder": "Ex: Blanc cassé, RAL 9010"}
        ),
    )
    couleur_plafond = forms.CharField(
        label=_("Couleur du plafond"),
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-input", "placeholder": "Ex: Blanc"}
        ),
    )
    couleur_boiseries = forms.CharField(
        label=_("Couleur des boiseries"),
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-input", "placeholder": "Ex: Blanc satin"}
        ),
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        logger.info(f"Inicializando ProjectForm para user: {self.user}")

        # Se editando, preencher campos customizados
        if self.instance and self.instance.pk:
            self._populate_custom_fields()

    def _populate_custom_fields(self):
        """Preenche campos customizados com dados existentes."""
        # Tipos de pièces
        if self.instance.types_pieces:
            for piece in self.instance.types_pieces:
                field_name = f"pieces_{piece}"
                if field_name in self.fields:
                    self.initial[field_name] = True

        # Couleurs
        if self.instance.couleurs_souhaitees:
            couleurs = self.instance.couleurs_souhaitees
            self.initial["couleur_murs"] = couleurs.get("murs", "")
            self.initial["couleur_plafond"] = couleurs.get("plafond", "")
            self.initial["couleur_boiseries"] = couleurs.get("boiseries", "")

    def clean_code_postal(self):
        """Validação do código postal."""
        code_postal = self.cleaned_data.get("code_postal")
        if code_postal:
            # Validação básica para código postal francês
            if not re.match(r"^\d{5}$", code_postal):
                raise ValidationError(_("Le code postal doit contenir 5 chiffres."))
        return code_postal

    def clean_contact_telephone(self):
        """Validação do telefone de contato."""
        telephone = self.cleaned_data.get("contact_telephone")
        if telephone:
            # Remover espaços e caracteres especiais para validação
            phone_clean = re.sub(r"[^\d+]", "", telephone)
            if not re.match(r"^\+?[1-9]\d{1,14}$", phone_clean):
                raise ValidationError(_("Numéro de téléphone invalide."))
        return telephone

    def clean_surface_totale(self):
        """Validação da superfície total."""
        surface = self.cleaned_data.get("surface_totale")
        if surface is not None and surface <= 0:
            raise ValidationError(_("La surface totale doit être supérieure à 0."))
        return surface

    def clean(self):
        """Validações globais do formulário."""
        cleaned_data = super().clean()

        # Validar datas
        date_debut = cleaned_data.get("date_debut_souhaitee")
        date_fin = cleaned_data.get("date_fin_souhaitee")

        if date_debut and date_fin:
            if date_debut > date_fin:
                raise ValidationError(
                    {"date_fin_souhaitee": _("La date de fin doit être postérieure à la date de début.")}
                )

        # Validar budget
        budget_min = cleaned_data.get("budget_minimum")
        budget_max = cleaned_data.get("budget_maximum")

        if budget_min and budget_max:
            if budget_min > budget_max:
                raise ValidationError(
                    {"budget_maximum": _("Le budget maximum doit être supérieur au budget minimum.")}
                )

        # Validar superfícies
        surface_totale = cleaned_data.get("surface_totale")
        surface_murs = cleaned_data.get("surface_murs")
        surface_plafond = cleaned_data.get("surface_plafond")

        if surface_totale and surface_murs and surface_plafond:
            if (surface_murs + surface_plafond) > (surface_totale * 3):  # Tolerância
                self.add_error(
                    "surface_totale",
                    _("La surface totale semble incohérente avec les surfaces détaillées."),
                )

        return cleaned_data

    def save(self, commit=True):
        """Salvamento personalizado."""
        logger.info(f"Salvando projeto para user: {self.user}")

        project = super().save(commit=False)

        # Definir o usuário
        if self.user:
            project.user = self.user

        # Processar tipos de pièces
        types_pieces = []
        piece_fields = [
            "pieces_salon",
            "pieces_cuisine",
            "pieces_chambre",
            "pieces_salle_de_bain",
            "pieces_bureau",
            "pieces_couloir",
            "pieces_exterieur",
        ]

        for field in piece_fields:
            if self.cleaned_data.get(field):
                piece_type = field.replace("pieces_", "")
                types_pieces.append(piece_type)

        project.types_pieces = types_pieces

        # Processar couleurs
        couleurs = {}
        if self.cleaned_data.get("couleur_murs"):
            couleurs["murs"] = self.cleaned_data["couleur_murs"]
        if self.cleaned_data.get("couleur_plafond"):
            couleurs["plafond"] = self.cleaned_data["couleur_plafond"]
        if self.cleaned_data.get("couleur_boiseries"):
            couleurs["boiseries"] = self.cleaned_data["couleur_boiseries"]

        project.couleurs_souhaitees = couleurs

        if commit:
            project.save()
            logger.info(f"Projeto salvo: {project.reference}")

        return project


class ProjectStatusForm(forms.ModelForm):
    """
    Formulário para atualização de status (apenas admin).
    """

    class Meta:
        model = Project
        fields = ["status", "assigned_to", "notes_internes"]
        widgets = {
            "status": forms.Select(attrs={"class": "form-select"}),
            "assigned_to": forms.Select(attrs={"class": "form-select"}),
            "notes_internes": forms.Textarea(
                attrs={
                    "class": "form-textarea",
                    "rows": 4,
                    "placeholder": "Notes internes...",
                }
            ),
        }


class DevisForm(forms.ModelForm):
    """
    Formulário para criação e edição de devis.
    """

    class Meta:
        model = Devis
        fields = [
            "title",
            "description",
            "date_expiry",
            "tax_rate",
            "terms_conditions",
            "notes",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-input", "placeholder": "Titre du devis"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-textarea",
                    "rows": 4,
                    "placeholder": "Description des travaux proposés...",
                }
            ),
            "date_expiry": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "tax_rate": forms.NumberInput(
                attrs={"class": "form-input", "step": "0.01", "min": "0", "max": "100", "placeholder": "20.00"}
            ),
            "terms_conditions": forms.Textarea(
                attrs={
                    "class": "form-textarea",
                    "rows": 6,
                    "placeholder": "Conditions générales...",
                }
            ),
            "notes": forms.Textarea(
                attrs={"class": "form-textarea", "rows": 3, "placeholder": "Notes additionnelles..."}
            ),
        }

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop("project", None)
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Definir data de expiração padrão (30 dias)
        if not self.initial.get("date_expiry"):
            from datetime import date, timedelta

            self.initial["date_expiry"] = date.today() + timedelta(days=30)

    def clean_date_expiry(self):
        """Validação da data de expiração."""
        date_expiry = self.cleaned_data.get("date_expiry")
        if date_expiry:
            from datetime import date

            if date_expiry <= date.today():
                raise ValidationError(_("La date d'expiration doit être dans le futur."))
        return date_expiry

    def save(self, commit=True):
        """Salvamento personalizado."""
        devis = super().save(commit=False)

        if self.project:
            devis.project = self.project
        if self.user:
            devis.created_by = self.user

        if commit:
            devis.save()

        return devis


class DevisLineForm(forms.ModelForm):
    """
    Formulário para linhas de devis.
    """

    class Meta:
        model = DevisLine
        fields = ["product", "quantity", "unit_price", "description"]
        widgets = {
            "product": forms.Select(attrs={"class": "form-select"}),
            "quantity": forms.NumberInput(
                attrs={"class": "form-input", "step": "0.01", "min": "0"}
            ),
            "unit_price": forms.NumberInput(
                attrs={"class": "form-input", "step": "0.01", "min": "0"}
            ),
            "description": forms.Textarea(
                attrs={"class": "form-textarea", "rows": 2, "placeholder": "Description spécifique..."}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Filtrar apenas produtos ativos
        self.fields["product"].queryset = Product.objects.filter(is_active=True)

        # Se há um produto selecionado, preencher preço
        if "product" in self.data:
            try:
                product_id = self.data.get("product")
                product = Product.objects.get(pk=product_id)
                if not self.data.get("unit_price"):
                    self.initial["unit_price"] = product.price_unit
            except (ValueError, Product.DoesNotExist):
                pass

    def clean_quantity(self):
        """Validação da quantidade."""
        quantity = self.cleaned_data.get("quantity")
        if quantity is not None and quantity <= 0:
            raise ValidationError(_("La quantité doit être supérieure à 0."))
        return quantity

    def clean_unit_price(self):
        """Validação do preço unitário."""
        unit_price = self.cleaned_data.get("unit_price")
        if unit_price is not None and unit_price < 0:
            raise ValidationError(_("Le prix unitaire ne peut pas être négatif."))
        return unit_price


class ProductForm(forms.ModelForm):
    """
    Formulário para criação e edição de produtos (admin).
    """

    class Meta:
        model = Product
        fields = ["name", "description", "type_product", "unit", "price_unit", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-input", "placeholder": "Nom du produit"}),
            "description": forms.Textarea(
                attrs={"class": "form-textarea", "rows": 3, "placeholder": "Description du produit..."}
            ),
            "type_product": forms.Select(attrs={"class": "form-select"}),
            "unit": forms.Select(attrs={"class": "form-select"}),
            "price_unit": forms.NumberInput(
                attrs={"class": "form-input", "step": "0.01", "min": "0", "placeholder": "0.00"}
            ),
            "is_active": forms.CheckboxInput(attrs={"class": "form-checkbox"}),
        }

    def clean_price_unit(self):
        """Validação do preço unitário."""
        price = self.cleaned_data.get("price_unit")
        if price is not None and price < 0:
            raise ValidationError(_("Le prix ne peut pas être négatif."))
        return price


class DevisStatusForm(forms.ModelForm):
    """
    Formulário para mudança de status do devis (cliente).
    """

    class Meta:
        model = Devis
        fields = ["status"]
        widgets = {"status": forms.HiddenInput()}

    response_comment = forms.CharField(
        label=_("Commentaire"),
        widget=forms.Textarea(
            attrs={"class": "form-textarea", "rows": 4, "placeholder": "Votre commentaire (optionnel)...",}
        ),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        self.action = kwargs.pop("action", None)  # 'accept' ou 'refuse'
        super().__init__(*args, **kwargs)

        if self.action == "accept":
            self.initial["status"] = Devis.Status.ACCEPTED
        elif self.action == "refuse":
            self.initial["status"] = Devis.Status.REFUSED


# ================================
# FORMSETS
# ================================

from django.forms import inlineformset_factory

DevisLineFormSet = inlineformset_factory(
    Devis,
    DevisLine,
    form=DevisLineForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)


# ================================
# FORM FILTERS
# ================================

class ProjectFilterForm(forms.Form):
    """
    Formulário para filtros na listagem de projetos.
    """

    search = forms.CharField(
        label=_("Recherche"),
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-input", "placeholder": "Rechercher..."}),
    )

    status = forms.ChoiceField(
        label=_("Statut"),
        choices=[("", _("Tous les statuts"))] + Project.Status.choices,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    type_projet = forms.ChoiceField(
        label=_("Type"),
        choices=[("", _("Tous les types"))] + Project.ProjectType.choices,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    priority = forms.ChoiceField(
        label=_("Priorité"),
        choices=[("", _("Toutes les priorités"))] + Project.Priority.choices,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    date_from = forms.DateField(
        label=_("Date début"),
        required=False,
        widget=forms.DateInput(attrs={"class": "form-input", "type": "date"}),
    )

    date_to = forms.DateField(
        label=_("Date fin"),
        required=False,
        widget=forms.DateInput(attrs={"class": "form-input", "type": "date"}),
    )


class DevisFilterForm(forms.Form):
    """
    Formulário para filtros na listagem de devis.
    """

    search = forms.CharField(
        label=_("Recherche"),
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-input", "placeholder": "Rechercher..."}),
    )

    status = forms.ChoiceField(
        label=_("Statut"),
        choices=[("", _("Tous les statuts"))] + Devis.Status.choices,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    project = forms.ModelChoiceField(
        label=_("Projet"),
        queryset=Project.objects.none(),
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user:
            # Filtrar projetos do usuário
            self.fields["project"].queryset = Project.objects.filter(user=user)
            self.fields["project"].choices = [("", _("Tous les projets"))] + [
                (p.pk, str(p)) for p in self.fields["project"].queryset
            ]
