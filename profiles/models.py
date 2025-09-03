from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """
    Modelo de perfil de usuário estendido.
    Contém informações complementares ao modelo User básico.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name=_("Utilisateur"),
    )

    # Avatar
    avatar = models.ImageField(
        _("Photo de profil"),
        upload_to="avatars/%Y/%m/",
        null=True,
        blank=True,
    )

    # Informações de contato
    phone_regex = RegexValidator(
        regex=r"^\+?1?\d{9,15}$",
        message=_(
            "Le numéro de téléphone doit être au format: '+999999999'. Jusqu'à 15 chiffres autorisés."
        ),
    )
    phone = models.CharField(
        _("Téléphone"),
        validators=[phone_regex],
        max_length=17,
        blank=True,
    )

    # Adresse
    address = models.TextField(
        _("Adresse"), blank=True, help_text=_("Adresse postale complète")
    )

    # Informações pessoais
    bio = models.TextField(
        _("Biographie"),
        blank=True,
        max_length=500,
        help_text=_("Description personnelle (max 500 caractères)"),
    )

    date_of_birth = models.DateField(
        _("Date de naissance"), null=True, blank=True, help_text=_("Format: JJ/MM/AAAA")
    )

    # Metadados
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)

    class Meta:
        verbose_name = _("Profil utilisateur")
        verbose_name_plural = _("Profils utilisateurs")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Profil de {self.user.get_full_name()}"

    @property
    def age(self):
        """Calcule l'âge à partir de la date de naissance."""
        if self.date_of_birth:
            today = timezone.now().date()
            return (
                today.year
                - self.date_of_birth.year
                - (
                    (today.month, today.day)
                    < (self.date_of_birth.month, self.date_of_birth.day)
                )
            )
        return None

    def get_avatar_url(self):
        """Retorna URL do avatar."""
        if self.avatar:
            return self.avatar.url
        return "/static/images/default-avatar.png"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """Cria perfil automaticamente."""
    if created:
        UserProfile.objects.create(user=instance)
    elif not hasattr(instance, "profile"):
        UserProfile.objects.create(user=instance)
