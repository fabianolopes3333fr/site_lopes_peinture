from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import uuid
from django.core.validators import RegexValidator
from django.utils.functional import cached_property


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_("The Email field must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    class AccountType(models.TextChoices):
        CLIENT = "CLIENT", _("Client")
        COLLABORATOR = "COLLABORATOR", _("Collaborateur")
        ADMINISTRATOR = "ADMINISTRATOR", _("Administrateur")

    # Adicione este campo ao modelo User
    account_type = models.CharField(
        _("type de compte"),
        max_length=20,
        choices=AccountType.choices,
        default=AccountType.CLIENT,
        help_text=_("Définit le niveau d'accès de l'utilisateur"),
    )

    email = models.EmailField(
        _("email address"),
        unique=True,
        db_index=True,  # Add index
        error_messages={
            "unique": _("A user with that email already exists."),
        },
    )

    # User Type Choice
    class UserType(models.TextChoices):
        INDIVIDUAL = "PARTICULAR", _("Particulier")
        PROFESSIONAL = "PROFESSIONAL", _("Professionnel")

    # Civility Choice
    class Civility(models.TextChoices):
        MR = "M", _("M")
        MRS = "MME", _("Mme")
        OTHER = "OTHER", _("Autre")

    # New fields for user type and personal info
    user_type = models.CharField(
        _("type d'utilisateur"),
        max_length=20,
        choices=UserType.choices,
        default=UserType.INDIVIDUAL,
    )
    civility = models.CharField(
        _("civilité"), max_length=5, choices=Civility.choices, default=Civility.MR
    )

    # Professional specific fields
    company_name = models.CharField(_("raison sociale"), max_length=255, blank=True)
    trading_name = models.CharField(_("nom commercial"), max_length=255, blank=True)
    siren = models.CharField(
        _("SIREN"), max_length=9, blank=True, help_text=_("9 caractères numériques")
    )
    vat_number = models.CharField(
        _("TVA Intracommunautaire"),
        max_length=14,
        blank=True,
        help_text=_("Format: FR + 11 caractères"),
    )
    legal_form = models.CharField(_("forme juridique"), max_length=100, blank=True)
    activity_type = models.CharField(_("type d'activité"), max_length=100, blank=True)
    ape_code = models.CharField(
        _("code APE"),
        max_length=5,
        blank=True,
        help_text=_("Code NAF/APE (5 caractères)"),
    )
    # Address fields
    billing_address = models.TextField(_("adresse de facturation"), blank=True)
    address_complement = models.CharField(
        _("complément d'adresse"), max_length=255, blank=True
    )
    country = models.CharField(_("pays"), max_length=100, default="France")

    first_name = models.CharField(_("first name"), max_length=150, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    verification_token = models.UUIDField(
        default=uuid.uuid4, editable=False, null=True, blank=True
    )
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    failed_login_attempts = models.PositiveIntegerField(default=0)
    last_failed_login = models.DateTimeField(null=True, blank=True)
    password_changed_at = models.DateTimeField(null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    # Add field dependencies
    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ["-date_joined"]
        constraints = [
            # Professional fields are required for professional accounts
            models.CheckConstraint(
                check=(
                    models.Q(user_type="PARTICULAR")
                    | (
                        models.Q(user_type="PROFESSIONAL")
                        & ~models.Q(company_name="")
                        & ~models.Q(siren="")
                    )
                ),
                name="professional_fields_required",
            )
        ]

    def __str__(self):
        return self.email

    # Add validators for specific fields
    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

        # Validate SIREN format
        if self.siren and not self.siren.isdigit():
            raise ValidationError(
                {"siren": _("Le SIREN doit contenir uniquement des chiffres.")}
            )

        # Validate VAT number format
        if self.vat_number and not self.vat_number.startswith("FR"):
            raise ValidationError(
                {"vat_number": _("Le numéro de TVA doit commencer par FR.")}
            )

    def is_professional(self):
        """Check if user is a professional account"""
        return self.user_type == self.UserType.PROFESSIONAL

    # Update the get_full_name method to include civility
    def get_full_name(self):
        """Return the full name, including civility"""
        parts = [self.get_civility_display()]
        if self.first_name:
            parts.append(self.first_name)
        if self.last_name:
            parts.append(self.last_name)
        return " ".join(parts).strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def increment_failed_login(self, ip_address):
        """Increment failed login attempts and log IP"""
        self.failed_login_attempts += 1
        self.last_failed_login = timezone.now()
        self.last_login_ip = ip_address
        self.save(
            update_fields=[
                "failed_login_attempts",
                "last_failed_login",
                "last_login_ip",
            ]
        )

    def reset_failed_login(self):
        """Reset failed login attempts counter"""
        self.failed_login_attempts = 0
        self.save(update_fields=["failed_login_attempts"])

    def is_locked_out(self):
        """Check if user is locked out due to too many failed attempts"""
        if self.failed_login_attempts >= settings.MAX_FAILED_LOGIN_ATTEMPTS:
            if self.last_failed_login:
                lockout_period = timezone.now() - timezone.timedelta(minutes=30)
                return self.last_failed_login >= lockout_period
        return False

    @cached_property
    def full_name(self):
        """Cached property for full name to avoid multiple db calls"""
        return self.get_full_name()

    def save(self, *args, **kwargs):
        """Override save to perform cleaning before saving"""
        self.clean()
        super().save(*args, **kwargs)

    @property
    def is_admin(self):
        """Check if user is an administrator"""
        return self.account_type == self.AccountType.ADMINISTRATOR

    @property
    def is_collaborator(self):
        """Check if user is a collaborator"""
        return self.account_type == self.AccountType.COLLABORATOR



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
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="projects",
        verbose_name=_("Utilisateur"),
    )
    type_projet = models.CharField(
        _("Type de projet"),
        max_length=50,
        choices=ProjectType.choices,
    )
    description = models.TextField(
        _("Description"), help_text=_("Décrivez votre projet en détail")
    )
    surface = models.DecimalField(
        _("Surface (m²)"),
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )
    date_debut_souhaitee = models.DateField(
        _("Date de début souhaitée"), null=True, blank=True
    )
    date_fin_souhaitee = models.DateField(
        _("Date de fin souhaitée"), null=True, blank=True
    )
    urgence = models.CharField(
        _("Urgence"),
        max_length=20,
        choices=Urgency.choices,
        default=Urgency.NORMAL,
    )
    adresse_travaux = models.CharField(
        _("Adresse des travaux"),  # This is the verbose_name
        max_length=255,
        # Remove duplicate verbose_name="Adresse du projet"
    )
    complement_adresse = models.CharField(
        _("Complément d'adresse"), max_length=255, blank=True
    )
    code_postal = models.CharField(
        _("Code postal"),
        max_length=10,
        # Remove duplicate verbose_name="Code postal"
    )
    ville = models.CharField(
        _("Ville"),
        max_length=100,
        # Remove duplicate verbose_name="Ville du projet"
    )
    pays = models.CharField(
        _("Pays"),
        max_length=100,
        default="France",
        # Remove duplicate verbose_name="Pays"
    )
    budget_estime = models.DecimalField(
        _("Budget estimé (€)"),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )
    status = models.CharField(
        _("Statut"),
        max_length=20,
        choices=Status.choices,
        default=Status.THINKING,
    )
    created_at = models.DateTimeField(
        _("Créé le"),
        auto_now_add=True,
        # Remove duplicate verbose_name="Date de création"
    )
    updated_at = models.DateTimeField(
        _("Mis à jour le"),
        auto_now=True,
        # Remove duplicate verbose_name="Dernière modification"
    )

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
