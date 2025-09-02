from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class Project(models.Model):
    """Informações sobre projetos do cliente"""

    class ProjectType(models.TextChoices):
        INTERIOR = "peinture_interieure", _("Peinture Intérieure")
        EXTERIOR = "peinture_exterieure", _("Peinture Extérieure")
        DECORATION = "decoration", _("Décoration")
        RENOVATION = "renovation", _("Rénovation")
        WALL_COVERING = "revetement_mural", _("Revêtement Mural")
        COMMERCIAL = "commercial", _("Peinture Commerciale")
        OTHER = "autre", _("Autre")

    class Status(models.TextChoices):
        THINKING = "en_reflexion", _("En réflexion")
        QUOTE_REQUESTED = "devis_demande", _("Devis demandé")
        QUOTE_RECEIVED = "devis_recu", _("Devis reçu")
        ACCEPTED = "accepte", _("Accepté")
        IN_PROGRESS = "en_cours", _("En cours")
        COMPLETED = "termine", _("Terminé")
        CANCELLED = "annule", _("Annulé")

    class Urgency(models.TextChoices):
        LOW = "faible", _("Faible")
        NORMAL = "normale", _("Normale")
        HIGH = "elevee", _("Élevée")
        URGENT = "urgente", _("Urgente")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="client_projects",
        verbose_name=_("Utilisateur"),
    )
    type_projet = models.CharField(
        verbose_name=_("Type de projet"),
        max_length=50,
        choices=ProjectType.choices,
    )
    description = models.TextField(
        verbose_name=_("Description"),
        help_text=_("Décrivez votre projet en détail"),
    )
    surface = models.DecimalField(
        verbose_name=_("Surface (m²)"),
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )
    date_debut_souhaitee = models.DateField(
        verbose_name=_("Date de début souhaitée"), null=True, blank=True
    )
    date_fin_souhaitee = models.DateField(
        verbose_name=_("Date de fin souhaitée"), null=True, blank=True
    )
    urgence = models.CharField(
        verbose_name=_("Urgence"),
        max_length=20,
        choices=Urgency.choices,
        default=Urgency.NORMAL,
    )
    adresse_travaux = models.CharField(
        verbose_name=_("Adresse des travaux"),
        max_length=255,
        default="À définir",
        help_text=_("Adresse où les travaux seront réalisés"),
    )
    complement_adresse = models.CharField(
        verbose_name=_("Complément d'adresse"), max_length=255, blank=True
    )
    code_postal = models.CharField(verbose_name=_("Code postal"), max_length=10)
    ville = models.CharField(verbose_name=_("Ville"), max_length=100)
    pays = models.CharField(verbose_name=_("Pays"), max_length=100, default="France")
    budget_estime = models.DecimalField(
        verbose_name=_("Budget estimé (€)"),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    status = models.CharField(
        verbose_name=_("Statut"),
        max_length=20,
        choices=Status.choices,
        default=Status.THINKING,
    )
    created_at = models.DateTimeField(verbose_name=_("Créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_("Mis à jour le"), auto_now=True)

    class Meta:
        verbose_name = _("projet")
        verbose_name_plural = _("projets")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.type_projet} - {self.user.get_full_name()} - {self.ville}"

    @property
    def is_active(self):
        """Check if project is currently active"""
        return self.status in [self.Status.ACCEPTED, self.Status.IN_PROGRESS]

    def can_be_edited(self):
        """Check if project can still be edited"""
        return self.status not in [self.Status.COMPLETED, self.Status.CANCELLED]

    def clean(self):
        """Validate project dates"""
        if self.date_fin_souhaitee and self.date_debut_souhaitee:
            if self.date_fin_souhaitee < self.date_debut_souhaitee:
                raise ValidationError(
                    {
                        "date_fin_souhaitee": _(
                            "La date de fin ne peut pas être antérieure à la date de début."
                        )
                    }
                )
