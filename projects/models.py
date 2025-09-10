from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from decimal import Decimal
import uuid
import re
import logging

logger = logging.getLogger(__name__)


class Project(models.Model):
    """
    Modelo completo para gerenciamento de projetos de pintura.
    """

    class ProjectType(models.TextChoices):
        INTERIOR = "peinture_interieure", _("Peinture Intérieure")
        EXTERIOR = "peinture_exterieure", _("Peinture Extérieure")
        DECORATION = "decoration", _("Décoration")
        RENOVATION = "renovation", _("Rénovation")
        WALL_COVERING = "revetement_mural", _("Revêtement Mural")
        COMMERCIAL = "commercial", _("Peinture Commerciale")
        RESIDENTIAL = "residentiel", _("Résidentiel")
        OTHER = "autre", _("Autre")

    class Status(models.TextChoices):
        DRAFT = "brouillon", _("Brouillon")
        SUBMITTED = "soumis", _("Soumis")
        UNDER_REVIEW = "en_examen", _("En examen")
        QUOTE_REQUESTED = "devis_demande", _("Devis demandé")
        QUOTE_SENT = "devis_envoye", _("Devis envoyé")
        QUOTE_ACCEPTED = "devis_accepte", _("Devis accepté")
        QUOTE_REFUSED = "devis_refuse", _("Devis refusé")
        SCHEDULED = "planifie", _("Planifié")
        IN_PROGRESS = "en_cours", _("En cours")
        COMPLETED = "termine", _("Terminé")
        CANCELLED = "annule", _("Annulé")
        ON_HOLD = "en_attente", _("En attente")

    class Priority(models.TextChoices):
        LOW = "faible", _("Faible")
        NORMAL = "normale", _("Normale")
        HIGH = "elevee", _("Élevée")
        URGENT = "urgente", _("Urgente")

    class RoomType(models.TextChoices):
        LIVING_ROOM = "salon", _("Salon")
        KITCHEN = "cuisine", _("Cuisine")
        BEDROOM = "chambre", _("Chambre")
        BATHROOM = "salle_de_bain", _("Salle de bain")
        OFFICE = "bureau", _("Bureau")
        HALLWAY = "couloir", _("Couloir")
        BASEMENT = "sous_sol", _("Sous-sol")
        ATTIC = "grenier", _("Grenier")
        GARAGE = "garage", _("Garage")
        EXTERIOR = "exterieur", _("Extérieur")

    class SurfaceCondition(models.TextChoices):
        EXCELLENT = "excellent", _("Excellent")
        GOOD = "bon", _("Bon")
        FAIR = "moyen", _("Moyen")
        POOR = "mauvais", _("Mauvais")
        DAMAGED = "abime", _("Abîmé")

    class FinishType(models.TextChoices):
        MATTE = "mat", _("Mat")
        SATIN = "satin", _("Satin")
        SEMI_GLOSS = "semi_brillant", _("Semi-brillant")
        GLOSS = "brillant", _("Brillant")
        TEXTURED = "texture", _("Texturé")

    # ================================
    # IDENTIFICATION & RELATIONS
    # ================================
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="projects",
        verbose_name=_("Client"),
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_projects",
        verbose_name=_("Assigné à"),
        limit_choices_to={"is_staff": True},
    )

    # ================================
    # INFORMATIONS GÉNÉRALES
    # ================================
    title = models.CharField(
        _("Titre du projet"),
        max_length=200,
        blank=True,
        help_text=_("Titre descriptif du projet"),
    )

    reference = models.CharField(
        _("Référence"),
        max_length=20,
        unique=True,
        blank=True,
        help_text=_("Référence unique générée automatiquement"),
    )

    type_projet = models.CharField(
        _("Type de projet"), max_length=50, choices=ProjectType.choices, db_index=True
    )

    description = models.TextField(
        _("Description détaillée"),
        help_text=_("Description complète du projet et des attentes"),
    )

    # ================================
    # DÉTAILS TECHNIQUES COMPLETS
    # ================================

    # Surfaces
    surface_totale = models.DecimalField(
        _("Surface totale (m²)"),
        max_digits=8,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text=_("Surface totale à traiter"),
    )

    surface_murs = models.DecimalField(
        _("Surface murs (m²)"),
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Surface des murs à peindre"),
    )

    surface_plafond = models.DecimalField(
        _("Surface plafond (m²)"),
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Surface du plafond à peindre"),
    )

    hauteur_sous_plafond = models.DecimalField(
        _("Hauteur sous plafond (m)"),
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Hauteur sous plafond en mètres"),
    )

    # Pièces et types
    nombre_pieces = models.PositiveIntegerField(
        _("Nombre de pièces"),
        default=1,
        help_text=_("Nombre total de pièces concernées"),
    )

    types_pieces = models.JSONField(
        _("Types de pièces"),
        default=list,
        blank=True,
        help_text=_("Liste des types de pièces concernées"),
    )

    # État et préparation
    etat_support = models.CharField(
        _("État du support"),
        max_length=20,
        choices=SurfaceCondition.choices,
        default=SurfaceCondition.GOOD,
        help_text=_("État actuel des surfaces à traiter"),
    )

    preparation_necessaire = models.TextField(
        _("Préparation nécessaire"),
        blank=True,
        help_text=_("Travaux de préparation requis"),
    )

    # Finitions et matériaux
    type_finition = models.CharField(
        _("Type de finition"),
        max_length=20,
        choices=FinishType.choices,
        default=FinishType.MATTE,
        help_text=_("Type de finition souhaitée"),
    )

    couleurs_souhaitees = models.JSONField(
        _("Couleurs souhaitées"),
        default=dict,
        blank=True,
        help_text=_("Couleurs par zone (murs, plafond, etc.)"),
    )

    materiaux_specifiques = models.TextField(
        _("Matériaux spécifiques"),
        blank=True,
        help_text=_("Matériaux ou marques spécifiques demandés"),
    )

    # Contraintes
    acces_difficile = models.BooleanField(
        _("Accès difficile"),
        default=False,
        help_text=_("Accès difficile ou contraintes particulières"),
    )

    contraintes_horaires = models.TextField(
        _("Contraintes horaires"),
        blank=True,
        help_text=_("Contraintes d'horaires ou de planning"),
    )

    # ================================
    # DATES ET PLANNING
    # ================================
    date_debut_souhaitee = models.DateField(
        _("Date de début souhaitée"),
        null=True,
        blank=True,
        help_text=_("Date souhaitée pour commencer les travaux"),
    )

    date_fin_souhaitee = models.DateField(
        _("Date de fin souhaitée"),
        null=True,
        blank=True,
        help_text=_("Date souhaitée pour terminer les travaux"),
    )

    date_debut_prevue = models.DateField(
        _("Date de début prévue"), null=True, blank=True
    )

    date_fin_prevue = models.DateField(_("Date de fin prévue"), null=True, blank=True)

    date_debut_effective = models.DateField(
        _("Date de début effective"), null=True, blank=True
    )

    date_fin_effective = models.DateField(
        _("Date de fin effective"), null=True, blank=True
    )

    # ================================
    # ADRESSE ET CONTACT
    # ================================
    adresse_travaux = models.CharField(
        _("Adresse des travaux"),
        max_length=255,
        default="",
        help_text=_("Adresse complète où les travaux seront réalisés"),
    )

    complement_adresse = models.CharField(
        _("Complément d'adresse"),
        max_length=255,
        blank=True,
        help_text=_("Appartement, étage, bâtiment, etc."),
    )

    code_postal = models.CharField(
        _("Code postal"),
        db_index=True,
        max_length=10,
    )

    ville = models.CharField(_("Ville"), db_index=True, max_length=100)

    pays = models.CharField(_("Pays"), max_length=100, default="France")

    contact_nom = models.CharField(
        _("Nom du contact sur site"),
        max_length=200,
        blank=True,
        help_text=_("Personne à contacter sur le lieu des travaux"),
    )

    contact_telephone = models.CharField(
        _("Téléphone du contact"),
        max_length=20,
        blank=True,
        help_text=_("Numéro de téléphone du contact sur site"),
    )

    # ================================
    # BUDGET ET FINANCES
    # ================================
    budget_minimum = models.DecimalField(
        _("Budget minimum (€)"),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Budget minimum envisagé"),
    )

    budget_maximum = models.DecimalField(
        _("Budget maximum (€)"),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Budget maximum envisagé"),
    )

    # ================================
    # STATUT ET PRIORITÉ
    # ================================
    status = models.CharField(
        _("Statut"),
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )

    priority = models.CharField(
        _("Priorité"),
        max_length=20,
        choices=Priority.choices,
        default=Priority.NORMAL,
        db_index=True,
    )

    # ================================
    # NOTES ET COMMENTAIRES
    # ================================
    notes_client = models.TextField(
        _("Notes du client"),
        blank=True,
        help_text=_("Remarques et demandes spécifiques du client"),
    )

    notes_internes = models.TextField(
        _("Notes internes"), blank=True, help_text=_("Notes internes pour l'équipe")
    )

    # ================================
    # MÉTADONNÉES
    # ================================
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)
    completed_at = models.DateTimeField(_("Terminé le"), null=True, blank=True)

    class Meta:
        verbose_name = _("Projet")
        verbose_name_plural = _("Projets")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["type_projet", "status"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["priority", "status"]),
            models.Index(fields=["reference"]),
        ]

    def __str__(self):
        return f"[{self.reference}] {self.title}"

    def save(self, *args, **kwargs):
        # Gerar referência se não existir
        if not self.reference:
            self.reference = self.generate_reference()

        # Gerar título inteligente se não existir ou se ainda for o padrão

        if not self.title or self.title.startswith("Projet -"):
            if self.ville and self.type_projet:
                self.title = f"{self.get_type_projet_display()} - {self.ville}"
            elif self.type_projet:
                self.title = f"{self.get_type_projet_display()}"
            else:
                self.title = f"Projet - {timezone.now().strftime('%d/%m/%Y')}"

        super().save(*args, **kwargs)

    def generate_reference(self):
        """Gera uma referência única para o projeto."""
        import datetime

        year = datetime.datetime.now().year

        # Contar projetos do ano
        count = Project.objects.filter(created_at__year=year).count() + 1

        return f"PROJ-{year}-{count:04d}"

    def get_absolute_url(self):
        return reverse("projects:detail", kwargs={"pk": self.pk})

    @property
    def can_be_edited(self):
        """Verifica se o projeto pode ser editado."""
        readonly_statuses = [
            self.Status.COMPLETED,
            self.Status.CANCELLED,
            self.Status.IN_PROGRESS,
        ]
        return self.status not in readonly_statuses

    @property
    def can_request_quote(self):
        """Verifica se pode solicitar orçamento."""
        allowed_statuses = [
            self.Status.DRAFT,
            self.Status.SUBMITTED,
            self.Status.UNDER_REVIEW,
        ]
        return self.status in allowed_statuses

    @property
    def progress_percentage(self):
        """Calcula porcentagem de progresso."""
        progress_map = {
            self.Status.DRAFT: 5,
            self.Status.SUBMITTED: 15,
            self.Status.UNDER_REVIEW: 25,
            self.Status.QUOTE_REQUESTED: 35,
            self.Status.QUOTE_SENT: 50,
            self.Status.QUOTE_ACCEPTED: 70,
            self.Status.QUOTE_REFUSED: 30,
            self.Status.SCHEDULED: 80,
            self.Status.IN_PROGRESS: 90,
            self.Status.COMPLETED: 100,
            self.Status.CANCELLED: 0,
            self.Status.ON_HOLD: 40,
        }
        return progress_map.get(self.status, 0)


class Product(models.Model):
    """
    Modelo para produtos/serviços que podem ser incluídos nos devis.
    """

    class ProductType(models.TextChoices):
        PAINT = "peinture", _("Peinture")
        PRIMER = "sous_couche", _("Sous-couche")
        LABOR = "main_oeuvre", _("Main d'œuvre")
        MATERIAL = "materiel", _("Matériel")
        EQUIPMENT = "equipement", _("Équipement")
        SERVICE = "service", _("Service")
        OTHER = "autre", _("Autre")

    class Unit(models.TextChoices):
        M2 = "m2", _("m²")
        ML = "ml", _("ml")
        PIECE = "piece", _("Pièce")
        HOUR = "heure", _("Heure")
        DAY = "jour", _("Jour")
        LITER = "litre", _("Litre")
        KG = "kg", _("Kg")
        PACKAGE = "forfait", _("Forfait")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Informations produit
    code = models.CharField(
        _("Code produit"),
        max_length=50,
        unique=True,
        help_text=_("Code unique du produit"),
    )

    name = models.CharField(
        _("Nom du produit"), max_length=200, help_text=_("Nom commercial du produit")
    )

    description = models.TextField(
        _("Description"), blank=True, help_text=_("Description détaillée du produit")
    )

    type_product = models.CharField(
        _("Type de produit"), max_length=20, choices=ProductType.choices, db_index=True
    )

    # Prix et unités
    unit = models.CharField(
        _("Unité"),
        max_length=20,
        choices=Unit.choices,
        help_text=_("Unité de mesure pour ce produit"),
    )

    price_unit = models.DecimalField(
        _("Prix unitaire (€)"),
        max_digits=10,
        decimal_places=2,
        help_text=_("Prix par unité"),
    )

    # Gestion
    is_active = models.BooleanField(
        _("Actif"), default=True, help_text=_("Produit disponible pour les devis")
    )

    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

    class Meta:
        verbose_name = _("Produit")
        verbose_name_plural = _("Produits")
        ordering = ["type_product", "name"]

    def __str__(self):
        return f"[{self.code}] {self.name}"

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_code()
        super().save(*args, **kwargs)

    def generate_code(self):
        """Gera código único para o produto."""
        import datetime

        year = datetime.datetime.now().year % 100  # 2 dígitos
        count = Product.objects.count() + 1
        type_prefix = self.type_product[:3].upper()
        return f"{type_prefix}-{year}{count:04d}"

    # No modelo Project:
    def can_be_deleted(self):
        """Verificar se projeto pode ser deletado"""
        # Não pode deletar se tem devis enviados ou aceitos
        if self.devis.exclude(status="brouillon").exists():
            return False

        # Não pode deletar se está em execução
        if self.status in ["en_cours", "termine"]:
            return False

        # Pode deletar se é brouillon ou rejeitado
        return self.status in ["brouillon", "nouveau", "refuse"]


class Devis(models.Model):
    """
    Modelo para gerenciamento de devis (orçamentos).
    """

    class Status(models.TextChoices):
        DRAFT = "brouillon", _("Brouillon")
        SENT = "envoye", _("Envoyé")
        VIEWED = "vu", _("Vu par le client")
        ACCEPTED = "accepte", _("Accepté")
        REFUSED = "refuse", _("Refusé")
        EXPIRED = "expire", _("Expiré")
        CANCELLED = "annule", _("Annulé")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Relations
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="devis",
        verbose_name=_("Projet"),
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_devis",
        verbose_name=_("Créé par"),
    )

    # Informations devis
    reference = models.CharField(_("Référence"), max_length=20, unique=True, blank=True)

    title = models.CharField(
        _("Titre du devis"),
        max_length=200,
        blank=True,
        help_text=_("Titre descriptif du devis"),
    )

    description = models.TextField(
        _("Description"), blank=True, help_text=_("Description des travaux proposés")
    )

    # Dates et validité
    date_created = models.DateTimeField(_("Date de création"), auto_now_add=True)
    date_sent = models.DateTimeField(_("Date d'envoi"), null=True, blank=True)
    date_viewed = models.DateTimeField(_("Date de consultation"), null=True, blank=True)
    date_response = models.DateTimeField(_("Date de réponse"), null=True, blank=True)
    date_expiry = models.DateField(
        _("Date d'expiration"), help_text=_("Date limite de validité du devis")
    )

    # Statut
    status = models.CharField(
        _("Statut"),
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )

    # Montants
    subtotal = models.DecimalField(
        _("Sous-total (€)"), max_digits=10, decimal_places=2, default=Decimal("0.00")
    )

    tax_rate = models.DecimalField(
        _("Taux TVA (%)"), max_digits=5, decimal_places=2, default=Decimal("20.00")
    )

    tax_amount = models.DecimalField(
        _("Montant TVA (€)"), max_digits=10, decimal_places=2, default=Decimal("0.00")
    )

    total = models.DecimalField(
        _("Total TTC (€)"), max_digits=10, decimal_places=2, default=Decimal("0.00")
    )

    # Notes
    terms_conditions = models.TextField(
        _("Conditions générales"),
        blank=True,
        help_text=_("Conditions générales de vente et modalités"),
    )

    notes = models.TextField(
        _("Notes"), blank=True, help_text=_("Notes additionnelles")
    )

    # Métadonnées
    updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

    class Meta:
        verbose_name = _("Devis")
        verbose_name_plural = _("Devis")
        ordering = ["-date_created"]

    def __str__(self):
        return f"[{self.reference}] {self.title}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = self.generate_reference()

        # Gerar título inteligente se não existir ou se ainda for o padrão
        if not self.title or self.title.startswith("Devis -"):
            if self.project and self.project.title:
                self.title = f"Devis - {self.project.title}"
            elif self.project:
                self.title = f"Devis - {self.project.get_type_projet_display()}"
            else:
                self.title = f"Devis - {timezone.now().strftime('%d/%m/%Y')}"

        super().save(*args, **kwargs)

    # No modelo Devis:
    def can_be_deleted(self):
        """Verificar se devis pode ser deletado"""
        # Não pode deletar devis aceitos (exceto superuser)
        if self.status == "accepte":
            return False

        # Não pode deletar se projeto está em execução
        if self.project.status == "en_cours":
            return False

        # Pode deletar brouillons e alguns outros status
        return self.status in ["brouillon", "refuse"]

    def is_expired(self):
        """Verificar se devis expirou"""
        if not self.date_expiry:
            return False
        return timezone.now().date() > self.date_expiry

    def generate_reference(self):
        """Gera referência única para o devis."""
        import datetime

        year = datetime.datetime.now().year
        count = Devis.objects.filter(date_created__year=year).count() + 1
        return f"DEV-{year}-{count:04d}"

    def calculate_totals(self):
        """Calcula os totais do devis."""
        lines = self.lines.all()
        self.subtotal = sum(line.total for line in lines)
        self.tax_amount = self.subtotal * (self.tax_rate / 100)
        self.total = self.subtotal + self.tax_amount
        self.save(update_fields=["subtotal", "tax_amount", "total"])

    @property
    def is_expired(self):
        """Verifica se o devis expirou."""
        return self.date_expiry < timezone.now().date()

    @property
    def can_be_accepted(self):
        """Verifica se o devis pode ser aceito."""
        return (
            self.status in [self.Status.SENT, self.Status.VIEWED]
            and not self.is_expired
        )


class DevisLine(models.Model):
    """
    Linha de devis - cada item do orçamento.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    devis = models.ForeignKey(
        Devis, on_delete=models.CASCADE, related_name="lines", verbose_name=_("Devis")
    )

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, verbose_name=_("Produit")
    )

    # Quantités et prix
    quantity = models.DecimalField(
        _("Quantité"),
        max_digits=10,
        decimal_places=2,
        help_text=_("Quantité de ce produit"),
    )

    unit_price = models.DecimalField(
        _("Prix unitaire (€)"),
        max_digits=10,
        decimal_places=2,
        help_text=_("Prix unitaire au moment du devis"),
    )

    total = models.DecimalField(
        _("Total ligne (€)"),
        max_digits=10,
        decimal_places=2,
        help_text=_("Montant total de cette ligne"),
    )

    # Informations additionnelles
    description = models.TextField(
        _("Description"),
        blank=True,
        help_text=_("Description spécifique pour cette ligne"),
    )

    order = models.PositiveIntegerField(
        _("Ordre"), default=0, help_text=_("Ordre d'affichage dans le devis")
    )

    class Meta:
        verbose_name = _("Ligne de devis")
        verbose_name_plural = _("Lignes de devis")
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def save(self, *args, **kwargs):
        # Calculer le total
        self.total = self.quantity * self.unit_price
        super().save(*args, **kwargs)

        # Recalculer les totaux du devis
        self.devis.calculate_totals()


class DevisHistory(models.Model):
    """
    Histórico de mudanças nos devis.
    """

    class ActionType(models.TextChoices):
        CREATED = "created", _("Créé")
        SENT = "sent", _("Envoyé")
        VIEWED = "viewed", _("Consulté")
        ACCEPTED = "accepted", _("Accepté")
        REFUSED = "refused", _("Refusé")
        MODIFIED = "modified", _("Modifié")
        CANCELLED = "cancelled", _("Annulé")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    devis = models.ForeignKey(
        Devis, on_delete=models.CASCADE, related_name="history", verbose_name=_("Devis")
    )

    action = models.CharField(_("Action"), max_length=20, choices=ActionType.choices)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("Utilisateur"),
    )

    timestamp = models.DateTimeField(_("Date/Heure"), auto_now_add=True)

    notes = models.TextField(
        _("Notes"), blank=True, help_text=_("Notes sur cette action")
    )

    class Meta:
        verbose_name = _("Historique devis")
        verbose_name_plural = _("Historiques devis")
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.devis.reference} - {self.get_action_display()}"
