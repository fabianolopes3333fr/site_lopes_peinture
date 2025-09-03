from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from decimal import Decimal
import uuid


class Project(models.Model):
    """
    Modelo para gerenciamento de projetos de pintura.
    Contém informações detalhadas sobre projetos dos clientes.
    """

    class ProjectType(models.TextChoices):
        INTERIOR = "peinture_interieure", _("Peinture Intérieure")
        EXTERIOR = "peinture_exterieure", _("Peinture Extérieure")
        DECORATION = "decoration", _("Décoration")
        RENOVATION = "renovation", _("Rénovation")
        WALL_COVERING = "revetement_mural", _("Revêtement Mural")
        COMMERCIAL = "commercial", _("Peinture Commerciale")
        OTHER = "autre", _("Autre")

    class Status(models.TextChoices):
        DRAFT = "brouillon", _("Brouillon")
        THINKING = "en_reflexion", _("En réflexion")
        QUOTE_REQUESTED = "devis_demande", _("Devis demandé")
        QUOTE_RECEIVED = "devis_recu", _("Devis reçu")
        QUOTE_APPROVED = "devis_approuve", _("Devis approuvé")
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

    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Relations
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="client_projects",
        verbose_name=_("Client"),
    )

    # Informations du projet
    title = models.CharField(
        _("Titre du projet"),
        max_length=200,
        blank=True,  # Permitir vazio temporariamente
        help_text=_("Titre court et descriptif du projet"),
    )

    type_projet = models.CharField(
        _("Type de projet"), max_length=50, choices=ProjectType.choices, db_index=True
    )

    description = models.TextField(
        _("Description"), help_text=_("Description détaillée du projet")
    )

    # Détails techniques
    surface = models.DecimalField(
        _("Surface (m²)"),
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Surface à traiter en mètres carrés"),
    )

    nombre_pieces = models.PositiveIntegerField(
        _("Nombre de pièces"),
        null=True,
        blank=True,
        help_text=_("Nombre de pièces concernées par le projet"),
    )

    # Dates
    date_debut_souhaitee = models.DateField(
        _("Date de début souhaitée"),
        null=True,
        blank=True,
        help_text=_("Date à laquelle vous souhaitez commencer les travaux"),
    )

    date_fin_souhaitee = models.DateField(
        _("Date de fin souhaitée"),
        null=True,
        blank=True,
        help_text=_("Date à laquelle vous souhaitez finir les travaux"),
    )

    date_debut_effective = models.DateField(
        _("Date de début effective"), null=True, blank=True
    )

    date_fin_effective = models.DateField(
        _("Date de fin effective"), null=True, blank=True
    )

    # Priorité et statut
    priority = models.CharField(
        _("Priorité"),
        max_length=20,
        choices=Priority.choices,
        default=Priority.NORMAL,
        db_index=True,
    )

    status = models.CharField(
        _("Statut"),
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )

    # Adresse des travaux
    adresse_travaux = models.CharField(
        _("Adresse des travaux"),
        max_length=255,
        help_text=_("Adresse où les travaux seront réalisés"),
    )

    complement_adresse = models.CharField(
        _("Complément d'adresse"),
        max_length=255,
        blank=True,
        help_text=_("Appartement, étage, bâtiment, etc."),
    )

    code_postal = models.CharField(_("Code postal"), max_length=10, db_index=True)

    ville = models.CharField(_("Ville"), max_length=100, db_index=True)

    pays = models.CharField(_("Pays"), max_length=100, default="France")

    # Informations financières
    budget_estime = models.DecimalField(
        _("Budget estimé (€)"),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Budget approximatif pour le projet"),
    )

    devis_montant = models.DecimalField(
        _("Montant du devis (€)"),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    # Notes et commentaires
    notes_client = models.TextField(
        _("Notes du client"), blank=True, help_text=_("Notes et remarques du client")
    )

    notes_internes = models.TextField(
        _("Notes internes"), blank=True, help_text=_("Notes internes pour l'équipe")
    )

    # Métadonnées
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
        ]
        permissions = [
            ("can_view_all_projects", "Peut voir tous les projets"),
            ("can_manage_projects", "Peut gérer tous les projets"),
            ("can_approve_quotes", "Peut approuver les devis"),
        ]

    def __str__(self):
        return f"{self.title} - {self.user.get_full_name()}"

    def get_absolute_url(self):
        """Retourne l'URL pour visualizar o projeto."""
        return reverse("projects:detail", kwargs={"pk": self.pk})

    # Properties de status
    @property
    def is_active(self):
        """Verifica se o projeto está ativo."""
        active_statuses = [
            self.Status.IN_PROGRESS,
            self.Status.SCHEDULED,
            self.Status.QUOTE_APPROVED,
        ]
        return self.status in active_statuses

    @property
    def is_completed(self):
        """Verifica se o projeto foi concluído."""
        return self.status == self.Status.COMPLETED

    @property
    def is_cancelled(self):
        """Verifica se o projeto foi cancelado."""
        return self.status == self.Status.CANCELLED

    @property
    def can_be_edited(self):
        """Verifica se o projeto ainda pode ser editado."""
        readonly_statuses = [self.Status.COMPLETED, self.Status.CANCELLED]
        return self.status not in readonly_statuses

    @property
    def duration_estimated(self):
        """Calcula a duração estimada do projeto em dias."""
        if self.date_debut_souhaitee and self.date_fin_souhaitee:
            return (self.date_fin_souhaitee - self.date_debut_souhaitee).days
        return None

    @property
    def duration_actual(self):
        """Calcula a duração real do projeto em dias."""
        if self.date_debut_effective and self.date_fin_effective:
            return (self.date_fin_effective - self.date_debut_effective).days
        return None

    @property
    def is_urgent(self):
        """Verifica se o projeto é urgente."""
        return self.priority == self.Priority.URGENT

    @property
    def is_overdue(self):
        """Verifica se o projeto está atrasado."""
        if self.date_fin_souhaitee and self.status not in [
            self.Status.COMPLETED,
            self.Status.CANCELLED,
        ]:
            return timezone.now().date() > self.date_fin_souhaitee
        return False

    @property
    def progress_percentage(self):
        """Calcula a porcentagem de progresso baseada no status."""
        progress_map = {
            self.Status.DRAFT: 5,
            self.Status.THINKING: 10,
            self.Status.QUOTE_REQUESTED: 25,
            self.Status.QUOTE_RECEIVED: 40,
            self.Status.QUOTE_APPROVED: 60,
            self.Status.SCHEDULED: 70,
            self.Status.IN_PROGRESS: 85,
            self.Status.COMPLETED: 100,
            self.Status.CANCELLED: 0,
            self.Status.ON_HOLD: 50,
        }
        return progress_map.get(self.status, 0)

    # Métodos de negócio
    def mark_as_completed(self):
        """Marca o projeto como concluído."""
        self.status = self.Status.COMPLETED
        self.completed_at = timezone.now()
        self.date_fin_effective = timezone.now().date()
        self.save(update_fields=["status", "completed_at", "date_fin_effective"])

    def cancel_project(self, reason=""):
        """Cancela o projeto."""
        self.status = self.Status.CANCELLED
        if reason:
            self.notes_internes += f"\n\nProjet annulé: {reason}"
        self.save(update_fields=["status", "notes_internes"])

    def estimate_cost_per_m2(self):
        """Calcula o custo estimado por metro quadrado."""
        if self.budget_estime and self.surface:
            return self.budget_estime / self.surface
        return None

    def clean(self):
        """Validações customizadas do modelo."""
        super().clean()

        # Gerar título automaticamente se não fornecido
        if not self.title:
            type_display = (
                self.get_type_projet_display() if self.type_projet else "Projet"
            )
            ville = self.ville if self.ville else "Non défini"
            self.title = f"{type_display} - {ville}"

        # Validar datas
        if self.date_fin_souhaitee and self.date_debut_souhaitee:
            if self.date_fin_souhaitee < self.date_debut_souhaitee:
                raise ValidationError(
                    {
                        "date_fin_souhaitee": _(
                            "La date de fin ne peut pas être antérieure à la date de début."
                        )
                    }
                )

        if self.date_fin_effective and self.date_debut_effective:
            if self.date_fin_effective < self.date_debut_effective:
                raise ValidationError(
                    {
                        "date_fin_effective": _(
                            "La date de fin effective ne peut pas être antérieure à la date de début effective."
                        )
                    }
                )

        # Validar orçamento
        if self.budget_estime and self.budget_estime <= 0:
            raise ValidationError({"budget_estime": _("Le budget doit être positif.")})

        if self.devis_montant and self.devis_montant <= 0:
            raise ValidationError(
                {"devis_montant": _("Le montant du devis doit être positif.")}
            )

        # Validar superficie
        if self.surface and self.surface <= 0:
            raise ValidationError({"surface": _("La surface doit être positive.")})

    def save(self, *args, **kwargs):
        """Override do save para executar validações e lógica adicional."""
        # Executar validações
        self.full_clean()

        # Marcar data de conclusão se status mudou para concluído
        if self.status == self.Status.COMPLETED and not self.completed_at:
            self.completed_at = timezone.now()
            if not self.date_fin_effective:
                self.date_fin_effective = timezone.now().date()

        super().save(*args, **kwargs)
