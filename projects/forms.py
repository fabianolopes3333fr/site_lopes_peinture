from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms import formset_factory
from .models import Project, Product, Devis, DevisLine


class ProjectStep1Form(forms.ModelForm):
    """Formulaire étape 1: Informations générales"""

    class Meta:
        model = Project
        fields = [
            "title",
            "description",
            "project_type",
            "surface_totale",
            "nombre_pieces",
            "types_pieces",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                    "placeholder": "Titre du projet",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                    "rows": 4,
                    "placeholder": "Description détaillée du projet",
                }
            ),
            "project_type": forms.Select(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                }
            ),
            "surface_totale": forms.NumberInput(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                    "placeholder": "Surface en m²",
                }
            ),
            "nombre_pieces": forms.NumberInput(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                    "placeholder": "Nombre de pièces",
                }
            ),
            "types_pieces": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                    "placeholder": "Ex: salon, cuisine, chambre...",
                }
            ),
        }


class ProjectStep2Form(forms.ModelForm):
    """Formulaire étape 2: Détails techniques"""

    class Meta:
        model = Project
        fields = [
            "etat_support",
            "type_finition",
            "materiaux_specifiques",
            "date_debut_souhaitee",
            "date_fin_souhaitee",
            "contraintes_horaires",
        ]
        widgets = {
            "etat_support": forms.Select(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                }
            ),
            "type_finition": forms.Select(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                }
            ),
            "materiaux_specifiques": forms.Textarea(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                    "rows": 3,
                    "placeholder": "Matériaux spécifiques requis",
                }
            ),
            "date_debut_souhaitee": forms.DateInput(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                    "type": "date",
                }
            ),
            "date_fin_souhaitee": forms.DateInput(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                    "type": "date",
                }
            ),
            "contraintes_horaires": forms.Textarea(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                    "rows": 3,
                    "placeholder": "Contraintes d'horaires ou d'accès",
                }
            ),
        }


class ProjectStep3Form(forms.ModelForm):
    """Formulaire étape 3: Contact et budget"""

    class Meta:
        model = Project
        fields = [
            "adresse_travaux",
            "complement_adresse",
            "code_postal",
            "ville",
            "contact_nom",
            "contact_telephone",
            "budget_minimum",
            "budget_maximum",
            "notes_client",
        ]
        widgets = {
            "adresse_travaux": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                    "placeholder": "Adresse complète des travaux",
                }
            ),
            "complement_adresse": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                    "placeholder": "Appartement, étage, bâtiment...",
                }
            ),
            "code_postal": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                    "placeholder": "Code postal",
                }
            ),
            "ville": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                    "placeholder": "Ville",
                }
            ),
            "contact_nom": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                    "placeholder": "Nom du contact principal",
                }
            ),
            "contact_telephone": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                    "placeholder": "Numéro de téléphone",
                }
            ),
            "budget_minimum": forms.NumberInput(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                    "placeholder": "Budget minimum en €",
                }
            ),
            "budget_maximum": forms.NumberInput(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                    "placeholder": "Budget maximum en €",
                }
            ),
            "notes_client": forms.Textarea(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                    "rows": 4,
                    "placeholder": "Informations supplémentaires du client",
                }
            ),
        }


class ProjectUpdateForm(forms.ModelForm):
    """Formulaire de mise à jour d'un projet"""

    def __init__(self, *args, **kwargs):
        # Extrair o parâmetro user se fornecido
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Aplicar classes CSS aos campos
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.TextInput):
                field.widget.attrs.update({"class": "form-input"})
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({"class": "form-textarea"})
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({"class": "form-select"})
            elif isinstance(field.widget, forms.DateInput):
                field.widget.attrs.update({"class": "form-input", "type": "date"})

    class Meta:
        model = Project
        fields = "__all__"
        exclude = ["reference", "created_at", "updated_at", "created_by"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-input"}),
            "description": forms.Textarea(attrs={"class": "form-textarea", "rows": 4}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "priority": forms.Select(attrs={"class": "form-select"}),
            "date_debut_souhaitee": forms.DateInput(
                attrs={"type": "date", "class": "form-input"}
            ),
            "date_fin_souhaitee": forms.DateInput(
                attrs={"type": "date", "class": "form-input"}
            ),
            "date_debut_prevue": forms.DateInput(
                attrs={"type": "date", "class": "form-input"}
            ),
            "date_fin_prevue": forms.DateInput(
                attrs={"type": "date", "class": "form-input"}
            ),
            "notes_internes": forms.Textarea(
                attrs={"class": "form-textarea", "rows": 3}
            ),
        }


# Alias para compatibilidade avec les vues
ProjectForm = ProjectUpdateForm


class ProduitForm(forms.ModelForm):
    """Formulaire pour les produits"""

    class Meta:
        model = Product
        fields = [
            "code",
            "name",
            "description",
            "type_produit",
            "price_unit",
            "unit",
            "is_active",
        ]
        widgets = {
            "code": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                    "placeholder": "Ex: PEIN-001",
                }
            ),
            "name": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                    "placeholder": "Nom du produit",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                    "rows": 3,
                    "placeholder": "Description du produit",
                }
            ),
            "type_produit": forms.Select(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                }
            ),
            "price_unit": forms.NumberInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "0.00",
                }
            ),
            "unit": forms.Select(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                }
            ),
            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # DEBUG: Print form initialization
        print(f"🔍 DEBUG ProduitForm __init__:")
        print(f"   Fields: {list(self.fields.keys())}")

        # CORREÇÃO: Definir choices manualmente se necessário
        from projects.models import ProductType, Unit

        # Verificar e corrigir choices do type_produit
        if hasattr(ProductType, "choices"):
            type_choices = ProductType.choices
            print(f"   type_produit choices (ProductType.choices): {type_choices}")
        else:
            # Fallback manual se choices não estiver funcionando
            type_choices = [
                ("paint", "Peinture"),
                ("material", "Matériau"),
                ("tool", "Outil"),
                ("service", "Service"),
            ]
            print(f"   type_produit choices (fallback): {type_choices}")

        # Aplicar choices ao campo
        self.fields["type_produit"].choices = type_choices

        # Verificar choices do unit
        if hasattr(Unit, "choices"):
            unit_choices = Unit.choices
            print(f"   unit choices: {unit_choices}")
        else:
            # Fallback manual
            unit_choices = [
                ("m2", "M²"),
                ("ml", "ML"),
                ("unite", "U"),
                ("piece", "Pièce"),
                ("heure", "Heure"),
                ("jour", "Jour"),
                ("litre", "Litre"),
                ("kg", "Kg"),
                ("forfait", "F"),
            ]
            print(f"   unit choices (fallback): {unit_choices}")

        # Aplicar choices ao campo
        self.fields["unit"].choices = unit_choices

        # Tornar campos obrigatórios
        required_fields = ["code", "name", "type_produit", "price_unit", "unit"]
        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].required = True

        # Valores padrão
        if "is_active" in self.fields:
            self.fields["is_active"].initial = True


class DevisLigneForm(forms.ModelForm):
    """Formulaire pour les lignes de devis"""

    class Meta:
        model = DevisLine
        fields = ["produit", "description", "quantity", "price_unit", "order"]
        widgets = {
            "produit": forms.Select(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                }
            ),
            "description": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                    "placeholder": "Description personnalisée",
                }
            ),
            "quantity": forms.NumberInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                    "step": "0.01",
                }
            ),
            "price_unit": forms.NumberInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                    "step": "0.01",
                }
            ),
            "order": forms.NumberInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md",
                    "min": "0",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["produit"].queryset = Product.objects.filter(is_active=True)
        # Se editing, auto-fill price_unit with product price
        if "produit" in self.data:
            try:
                produit_id = int(self.data.get("produit"))
                produit = Product.objects.get(pk=produit_id)
                if not self.data.get("price_unit"):
                    self.fields["price_unit"].initial = produit.price_unit
            except (ValueError, TypeError, Product.DoesNotExist):
                pass
