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
from accounts.models import User

logger = logging.getLogger(__name__)


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
    EN_ATTENTE = "en_attente", _("En attente")


class Priority(models.TextChoices):
    LOW = "faible", _("Faible")
    NORMAL = "normale", _("Normale")
    HIGH = "elevee", _("Élevée")
    URGENT = "urgente", _("Urgente")


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


class ProductType(models.TextChoices):
    PAINT = "peinture", _("Peinture")
    PRIMER = "sous_couche", _("Sous-couche")
    LABOR = "main_oeuvre", _("Main d'œuvre")
    MATERIAL = "materiel", _("Matériel")
    EQUIPMENT = "equipement", _("Équipement")
    SERVICE = "service", _("Service")
    OTHER = "autre", _("Autre")


class Unit(models.TextChoices):
    M2 = "m2", _("M²")
    ML = "ml", _("ML")
    UNIT = "unite", _("U")
    PIECE = "piece", _("Pièce")
    HOUR = "heure", _("Heure")
    DAY = "jour", _("Jour")
    LITER = "litre", _("Litre")
    KG = "kg", _("Kg")
    PACKAGE = "forfait", _("F")


class DevisStatus(models.TextChoices):
    DRAFT = "brouillon", _("Brouillon")
    SENT = "envoye", _("Envoyé")
    VIEWED = "vu", _("Vu par le client")
    ACCEPTED = "accepte", _("Accepté")
    REFUSED = "refuse", _("Refusé")
    EXPIRED = "expire", _("Expiré")
    CANCELLED = "annule", _("Annulé")


class Project(models.Model):
    """
    Modelo completo para gerenciamento de projetos de pintura.
    """

    # ====
    # IDENTIFICATION & RELATIONS
    # ====
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # user = models.ForeignKey(
    #     settings.AUTH_USER_MODEL,
    #     on_delete=models.CASCADE,
    #     related_name="projects",
    #     verbose_name=_("Créé par"),
    # )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="projets",
        verbose_name="Créé par",
        null=True,
        blank=True,
    )

    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_projects",
        verbose_name=_("Assigné à"),
        limit_choices_to={"is_staff": True},
    )

    # ====
    # INFORMATIONS GÉNÉRALES
    # ====
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

    project_type = models.CharField(
        _("Type de projet"),
        max_length=50,
        choices=ProjectType.choices,
        db_index=True,
        default=ProjectType.INTERIOR,
    )

    description = models.TextField(
        _("Description détaillée"),
        help_text=_("Description complète du projet et des attentes"),
    )

    # ====
    # DÉTAILS TECHNIQUES COMPLETS
    # ====

    # Surfaces
    surface_totale = models.DecimalField(
        _("Surface totale (m²)"),
        max_digits=8,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text=_("Surface totale à traiter"),
    )

    # Pièces et types
    nombre_pieces = models.IntegerField(
        _("Nombre de pièces"),
        default=1,
        help_text=_("Nombre total de pièces concernées"),
    )

    types_pieces = models.CharField(
        _("Types de pièces"),
        max_length=200,
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

    # ====
    # DATES ET PLANNING
    # ====
    contraintes_horaires = models.TextField(
        _("Contraintes horaires"),
        blank=True,
        help_text=_("Contraintes d'horaires ou de planning"),
    )
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

    # ====
    # ADRESSE ET CONTACT
    # ====
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

    # ====
    # BUDGET ET FINANCES
    # ====
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

    # ====
    # STATUT ET PRIORITÉ
    # ====
    status = models.CharField(
        _("Statut"),
        max_length=20,
        choices=Status.choices,
        default=Status.EN_ATTENTE,
        db_index=True,
    )

    priority = models.CharField(
        _("Priorité"),
        max_length=20,
        choices=Priority.choices,
        default=Priority.NORMAL,
        db_index=True,
    )

    # ====
    # NOTES ET COMMENTAIRES
    # ====
    notes_client = models.TextField(
        _("Notes du client"),
        blank=True,
        help_text=_("Remarques et demandes spécifiques du client"),
    )

    notes_internes = models.TextField(
        _("Notes internes"), blank=True, help_text=_("Notes internes pour l'équipe")
    )

    # ====
    # MÉTADONNÉES
    # ====
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)
    completed_at = models.DateTimeField(_("Terminé le"), null=True, blank=True)

    class Meta:
        verbose_name = _("Projet")
        verbose_name_plural = _("Projets")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["created_by", "status"]),  # era "user"
            models.Index(fields=["project_type", "status"]),  # era "type_projet"
            models.Index(fields=["created_at"]),
            models.Index(fields=["priority", "status"]),
            models.Index(fields=["reference"]),
        ]

    def __str__(self):
        return f"[{self.reference}] {self.title}"

    def generate_reference(self):
        """Gera uma referência única para o projeto."""
        import datetime

        year = datetime.datetime.now().year
        count = Project.objects.filter(created_at__year=year).count() + 1
        return f"PROJ-{year}-{count:04d}"

    def get_absolute_url(self):
        return reverse("projects:detail", kwargs={"pk": self.pk})

    @property
    def can_be_edited(self):
        """Verifica se o projeto pode ser editado."""
        readonly_statuses = [
            Status.COMPLETED,
            Status.CANCELLED,
            Status.IN_PROGRESS,
        ]
        return self.status not in readonly_statuses

    @property
    def can_request_quote(self):
        """Verifica se pode solicitar orçamento."""
        allowed_statuses = [
            Status.DRAFT,
            Status.SUBMITTED,
            Status.UNDER_REVIEW,
        ]
        return self.status in allowed_statuses

    @property
    def can_be_deleted(self):
        """Verificar se projeto pode ser deletado"""
        # Não pode deletar se tem devis enviados ou aceitos
        if hasattr(self, "devis") and self.devis.exclude(status=Status.DRAFT).exists():
            return False

        # Não pode deletar se está em execução
        if self.status in [Status.IN_PROGRESS, Status.COMPLETED]:
            return False

        # Pode deletar se é brouillon ou rejeitado
        return self.status in [Status.DRAFT, Status.SUBMITTED, Status.QUOTE_REFUSED]

    @property
    def progress_percentage(self):
        """Calcula porcentagem de progresso."""
        progress_map = {
            Status.DRAFT: 5,
            Status.SUBMITTED: 15,
            Status.UNDER_REVIEW: 25,
            Status.QUOTE_REQUESTED: 35,
            Status.QUOTE_SENT: 50,
            Status.QUOTE_ACCEPTED: 70,
            Status.QUOTE_REFUSED: 30,
            Status.SCHEDULED: 80,
            Status.IN_PROGRESS: 90,
            Status.COMPLETED: 100,
            Status.CANCELLED: 0,
            Status.EN_ATTENTE: 40,
        }
        return progress_map.get(self.status, 0)

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = self.generate_reference()  # Remover "PRJ-" duplicado
        super().save(*args, **kwargs)


class Product(models.Model):
    """
    Modelo para produtos/serviços que podem ser incluídos nos devis.
    """

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

    type_produit = models.CharField(
        _("Type de produit"), max_length=20, choices=ProductType.choices, db_index=True
    )

    # Prix et unités
    unit = models.CharField(
        _("Unité"),
        max_length=20,
        choices=Unit.choices,
        help_text=_("Unité de mesure pour ce produit"),
        default=Unit.M2,
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

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        ordering = ["name"]
        verbose_name = "Produit"
        verbose_name_plural = "Produits"

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_code()
        super().save(*args, **kwargs)

    def generate_code(self):
        """Gera código único para o produto."""
        import datetime

        year = datetime.datetime.now().year % 100  # 2 dígitos
        count = Product.objects.count() + 1
        type_prefix = self.type_produit[:3].upper()
        return f"{type_prefix}-{year}{count:04d}"


class Devis(models.Model):
    """
    Modelo para gerenciamento de devis (orçamentos).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Relations
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="devis",
        verbose_name=_("Projet"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_devis",
        verbose_name=_("Créé par"),
    )

    # Informations devis
    reference = models.CharField(max_length=50, unique=True, verbose_name="Référence")

    title = models.CharField(
        max_length=200,
        blank=True,
        help_text=_("Titre descriptif du devis"),
        verbose_name=_("Titre du devis"),
    )

    description = models.TextField(
        blank=True,
        help_text=_("Description des travaux proposés"),
        verbose_name=_("Description détaillée du devis"),
    )

    # Statut
    status = models.CharField(
        _("Statut"),
        max_length=20,
        choices=DevisStatus.choices,
        default=DevisStatus.DRAFT,
        db_index=True,
    )

    # Donnees de l'entreprise
    company_name = models.CharField(
        max_length=100,
        default="Ma Société",
        verbose_name=_("Nom de l'entreprise"),
    )
    company_address = models.CharField(
        max_length=255,
        default="123 Rue de l'Entreprise",
        verbose_name=_("Adresse de l'entreprise"),
    )
    company_siret = models.CharField(
        max_length=14,
        default="12345678901234",
        verbose_name=_("Numéro SIRET"),
    )
    company_postal_code = models.CharField(
        max_length=10,
        default="75001",
        verbose_name=_("Code postal de l'entreprise"),
    )
    company_city = models.CharField(
        max_length=100,
        default="Paris",
        verbose_name=_("Ville de l'entreprise"),
    )
    company_phone = models.CharField(
        max_length=20,
        default="01 23 45 67 89",
        verbose_name=_("Numéro de téléphone"),
    )
    company_email = models.EmailField(
        max_length=254,
        default="contact@entreprise.com",
        verbose_name=_("Email de l'entreprise"),
    )
    company_website = models.URLField(
        max_length=200,
        blank=True,
        default="https://www.entreprise.com",
        verbose_name=_("Site web de l'entreprise"),
    )
    company_logo = models.ImageField(
        upload_to="logos/",
        blank=True,
        verbose_name=_("Logo de l'entreprise"),
    )

    # Montants
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Sous-total"),
    )

    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("20.00"),
        verbose_name=_("Taux TVA"),
    )

    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Montant TVA"),
    )

    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Total TTC"),
    )

    # Notes
    terms_conditions = models.TextField(
        blank=True,
        help_text=_("Conditions générales de vente et modalités"),
        verbose_name=_("Conditions générales"),
    )

    notes = models.TextField(
        blank=True,
        help_text=_("Notes additionnelles"),
        verbose_name=_("Notes"),
    )

    # Métadonnées
    date_created = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Date de création")
    )
    date_updated = models.DateTimeField(
        auto_now=True, verbose_name=_("Date de modification")
    )
    date_sent = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Date d'envoi")
    )
    date_viewed = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Date de consultation")
    )
    date_accepted = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Date d'acceptation")
    )
    date_refused = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Date de refus")
    )
    date_expiry = models.DateField(
        null=True, blank=True, verbose_name=_("Date d'expiration")
    )

    class Meta:
        verbose_name = _("Devis")
        verbose_name_plural = _("Devis")
        ordering = ["-date_created"]

    def save(self, *args, **kwargs):
        if not self.reference:
            count = Devis.objects.count()
            self.reference = f"DEV-{timezone.now().year}-{count + 1:04d}"

        # Calcul des montants - Forcer tous les types en Decimal
        from decimal import Decimal

        # Assurer que tous les calculs utilisent des Decimal
        subtotal_decimal = (
            Decimal(str(self.subtotal)) if self.subtotal else Decimal("0")
        )
        tax_rate_decimal = (
            Decimal(str(self.tax_rate)) if self.tax_rate else Decimal("0")
        )

        # Calcul avec types consistents
        self.tax_amount = (subtotal_decimal * tax_rate_decimal) / Decimal("100")
        self.total = subtotal_decimal + self.tax_amount

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reference} - {self.title}"

    def generate_reference(self):
        """Génère une référence unique pour le devis"""
        from django.utils import timezone

        year = timezone.now().year
        count = Devis.objects.filter(date_created__year=year).count() + 1
        return f"DEV-{year}-{count:04d}"

    def calculate_totals(self):
        """Calcule les totaux du devis"""
        self.subtotal = sum(line.total for line in self.lines.all())
        self.tax_amount = self.subtotal * (self.tax_rate / 100)
        self.total = self.subtotal + self.tax_amount

    @property
    def is_expired(self):
        """Verifica se o devis expirou."""
        return self.date_expiry < timezone.now().date()

    @property
    def can_be_accepted(self):
        """Verifica se o devis pode ser aceito."""
        return (
            self.status in [DevisStatus.SENT, DevisStatus.VIEWED]
            and not self.is_expired
        )

    @property
    def can_be_deleted(self):
        """Verificar se devis pode ser deletado"""
        # Não pode deletar devis aceitos (exceto superuser)
        if self.status == DevisStatus.ACCEPTED:
            return False

        # Não pode deletar se projeto está em execução
        if self.project.status in [Status.IN_PROGRESS, Status.COMPLETED]:
            return False

        # Pode deletar brouillons e alguns outros status
        return self.status in [DevisStatus.DRAFT, DevisStatus.REFUSED]


class DevisLine(models.Model):
    """
    Linha de devis - cada item do orçamento.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    devis = models.ForeignKey(
        Devis, on_delete=models.CASCADE, related_name="lines", verbose_name=_("Devis")
    )

    produit = models.ForeignKey(
        Product, on_delete=models.CASCADE, verbose_name=_("Produit")
    )

    # Quantités et prix
    quantity = models.DecimalField(
        _("Quantité"),
        max_digits=10,
        decimal_places=2,
        help_text=_("Quantité de ce produit"),
    )

    price_unit = models.DecimalField(
        _("Prix unitaire (€)"),
        max_digits=10,
        decimal_places=2,
        help_text=_("Prix unitaire au moment du devis"),
    )

    total_line = models.DecimalField(
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
        return f"{self.devis.reference} - {self.produit.name}"

    def save(self, *args, **kwargs):
        # Calculer le total
        self.total_line = self.quantity * self.price_unit
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
