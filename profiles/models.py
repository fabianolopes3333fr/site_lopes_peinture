from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name=_("utilisateur"),
    )
    avatar = models.ImageField(
        _("photo de profil"), upload_to="avatars/", null=True, blank=True
    )
    phone = models.CharField(_("téléphone"), max_length=20, blank=True)
    address = models.TextField(_("adresse"), blank=True)
    bio = models.TextField(_("biographie"), blank=True)
    date_of_birth = models.DateField(_("date de naissance"), null=True, blank=True)
    created_at = models.DateTimeField(_("créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("mis à jour le"), auto_now=True)

    class Meta:
        verbose_name = _("profil utilisateur")
        verbose_name_plural = _("profils utilisateurs")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Profil de {self.user.email}"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """Cria automaticamente um perfil quando um usuário é criado"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    """Salva o perfil quando o usuário é salvo"""
    instance.profile.save()
