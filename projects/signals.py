from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Project, Devis, DevisHistory


@receiver(pre_save, sender=Project)
def project_pre_save(sender, instance, **kwargs):
    """Signal executado antes de salvar um projeto"""
    # Gerar referência se não existir
    if not instance.reference:
        instance.reference = instance.generate_reference()

    # Gerar título inteligente se não existir
    if not instance.title or instance.title.startswith("Projet -"):
        if instance.ville and instance.type_projet:
            instance.title = f"{instance.get_type_projet_display()} - {instance.ville}"
        elif instance.type_projet:
            instance.title = f"{instance.get_type_projet_display()}"
        else:
            instance.title = f"Projet - {timezone.now().strftime('%d/%m/%Y')}"


@receiver(post_save, sender=Project)
def project_post_save(sender, instance, created, **kwargs):
    """Signal executado após salvar um projeto"""
    if created:
        # Log da criação do projeto
        import logging

        logger = logging.getLogger("projects")
        logger.info(
            f"Novo projeto criado: {instance.reference} por {instance.user.email}"
        )


@receiver(post_save, sender=Devis)
def devis_post_save(sender, instance, created, **kwargs):
    """Signal executado após salvar um devis"""
    if created:
        # Criar entrada no histórico
        DevisHistory.objects.create(
            devis=instance,
            action=DevisHistory.ActionType.CREATED,
            user=instance.created_by,
            notes=f"Devis créé pour le projet {instance.project.title}",
        )

        # Log da criação do devis
        import logging

        logger = logging.getLogger("projects")
        logger.info(
            f"Novo devis criado: {instance.reference} para projeto {instance.project.reference}"
        )
