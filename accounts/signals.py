from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import User
from projects.models import Project
from profiles.models import UserProfile
from .permissions import CUSTOM_PERMISSIONS, create_custom_permissions


def setup_groups_and_permissions():
    """Configura os grupos e suas permissões"""

    # Primeiro, cria todas as permissões customizadas
    create_custom_permissions()

    # Define as permissões para cada grupo
    groups_permissions = {
        "Client": [
            "view_own_profile",
            "edit_own_profile",
            "view_own_projects",
            "edit_own_projects",
        ],
        "Collaborateur": [
            "view_own_profile",
            "edit_own_profile",
            "view_all_projects",
            "edit_all_projects",
            "manage_project_status",
            "view_statistics",
        ],
        "Administrateur": [
            "view_own_profile",
            "edit_own_profile",
            "view_all_profiles",
            "edit_all_profiles",
            "delete_profiles",
            "view_all_projects",
            "edit_all_projects",
            "delete_projects",
            "manage_project_status",
            "manage_collaborators",
            "view_statistics",
        ],
    }

    # Cria ou atualiza cada grupo com suas permissões
    for group_name, permission_codenames in groups_permissions.items():
        group, _ = Group.objects.get_or_create(name=group_name)

        # Limpa permissões existentes
        group.permissions.clear()

        # Adiciona as novas permissões
        for codename in permission_codenames:
            for model in [User, UserProfile, Project]:
                content_type = ContentType.objects.get_for_model(model)
                try:
                    permission = Permission.objects.get(
                        codename=codename, content_type=content_type
                    )
                    group.permissions.add(permission)
                except Permission.DoesNotExist:
                    continue


@receiver(post_migrate)
def create_groups_and_permissions(sender, **kwargs):
    """
    Signal para criar grupos e permissões após a migração
    """
    if sender.name == "accounts":
        setup_groups_and_permissions()


@receiver(post_save, sender=User)
def create_user_profile_and_add_to_group(sender, instance, created, **kwargs):
    """
    Signal para criar perfil de usuário e adicionar ao grupo apropriado
    """
    if created:
        # Cria o perfil do usuário
        UserProfile.objects.get_or_create(user=instance)

        # Mapeia o tipo de conta para o nome do grupo
        group_mapping = {
            User.AccountType.CLIENT: "Client",
            User.AccountType.COLLABORATOR: "Collaborateur",
            User.AccountType.ADMINISTRATOR: "Administrateur",
        }

        # Adiciona o usuário ao grupo apropriado
        group_name = group_mapping.get(instance.account_type)
        if group_name:
            group = Group.objects.get(name=group_name)
            instance.groups.add(group)

        # Se for administrador, marca como staff
        if instance.account_type == User.AccountType.ADMINISTRATOR:
            instance.is_staff = True
            instance.save(update_fields=["is_staff"])


def create_default_groups(sender, **kwargs):
    """Create default groups and permissions"""
    from .models import User  # Import here to avoid circular import

    # Your group creation logic here
    groups = {
        "Client": [],
        "Collaborateur": [],
        "Administrateur": [],
    }

    for group_name, permissions in groups.items():
        group, created = Group.objects.get_or_create(name=group_name)
