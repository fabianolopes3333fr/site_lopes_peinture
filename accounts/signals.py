import logging
from django.db.models.signals import post_save, post_migrate, pre_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
from .models import User

logger = logging.getLogger(__name__)


def create_custom_permissions():
    """
    Cria permissões customizadas para o sistema.
    """
    try:
        user_content_type = ContentType.objects.get_for_model(User)

        # Permissões customizadas específicas do nosso sistema
        custom_permissions = [
            ("view_own_profile", "Can view own profile"),
            ("edit_own_profile", "Can edit own profile"),
            ("delete_own_account", "Can delete own account"),
            ("view_all_users", "Can view all users"),
            ("edit_all_users", "Can edit all users"),
            ("delete_any_user", "Can delete any user"),
            ("manage_user_status", "Can activate/deactivate users"),
            ("view_admin_dashboard", "Can view admin dashboard"),
            ("export_user_data", "Can export user data"),
            ("view_security_logs", "Can view security logs"),
            ("manage_groups", "Can manage user groups"),
            ("send_notifications", "Can send notifications to users"),
        ]

        for codename, name in custom_permissions:
            permission, created = Permission.objects.get_or_create(
                codename=codename,
                content_type=user_content_type,
                defaults={"name": name},
            )
            if created:
                logger.info(f"Permissão criada: {codename}")

    except Exception as e:
        logger.error(f"Erro ao criar permissões customizadas: {str(e)}")


def setup_groups_and_permissions():
    """
    Configura os grupos e suas permissões baseado no user_type do modelo User.
    """
    try:
        # Primeiro, cria todas as permissões customizadas
        create_custom_permissions()

        # Define as permissões para cada grupo baseado no user_type
        groups_permissions = {
            "Clients": [
                "view_own_profile",
                "edit_own_profile",
                "delete_own_account",
                "export_user_data",
            ],
            "Collaborateurs": [
                "view_own_profile",
                "edit_own_profile",
                "delete_own_account",
                "export_user_data",
                "view_all_users",
                "send_notifications",
            ],
            "Super Administrateurs": [
                "view_own_profile",
                "edit_own_profile",
                "delete_own_account",
                "view_all_users",
                "edit_all_users",
                "delete_any_user",
                "manage_user_status",
                "view_admin_dashboard",
                "export_user_data",
                "view_security_logs",
                "manage_groups",
                "send_notifications",
            ],
        }

        user_content_type = ContentType.objects.get_for_model(User)

        # Cria ou atualiza cada grupo com suas permissões
        for group_name, permission_codenames in groups_permissions.items():
            group, created = Group.objects.get_or_create(name=group_name)

            if created:
                logger.info(f"Grupo criado: {group_name}")

            # Limpa permissões existentes do grupo
            group.permissions.clear()

            # Adiciona as novas permissões
            permissions_added = 0
            for codename in permission_codenames:
                try:
                    permission = Permission.objects.get(
                        codename=codename, content_type=user_content_type
                    )
                    group.permissions.add(permission)
                    permissions_added += 1
                except Permission.DoesNotExist:
                    logger.warning(f"Permissão não encontrada: {codename}")
                    continue

            logger.info(
                f"Grupo '{group_name}' configurado com {permissions_added} permissões"
            )

    except Exception as e:
        logger.error(f"Erro ao configurar grupos e permissões: {str(e)}")


@receiver(post_migrate)
def create_groups_and_permissions(sender, **kwargs):
    """
    Signal para criar grupos e permissões após as migrações.
    Executa apenas quando a app 'accounts' é migrada.
    """
    if sender.name == "accounts":
        logger.info("Configurando grupos e permissões após migração...")
        setup_groups_and_permissions()
        logger.info("Grupos e permissões configurados com sucesso!")


@receiver(pre_save, sender=User)
def user_pre_save(sender, instance, **kwargs):
    """
    Signal executado antes de salvar um usuário.
    """
    try:
        # Normaliza o email
        if instance.email:
            instance.email = instance.email.lower().strip()

        # Atualiza password_changed_at quando a senha é alterada
        if instance.pk:
            try:
                old_instance = User.objects.get(pk=instance.pk)
                # Se a senha mudou, atualizar password_changed_at
                if old_instance.password != instance.password:
                    instance.password_changed_at = timezone.now()

                # Armazena o tipo antigo para comparação posterior
                instance._old_user_type = old_instance.user_type
            except User.DoesNotExist:
                instance._old_user_type = None

        # Validações de integridade baseadas no user_type
        if instance.user_type == "superadmin":
            instance.is_staff = True
            instance.is_superuser = True
        elif instance.user_type == "collaborateur":
            instance.is_staff = True
            instance.is_superuser = False
        else:  # client
            instance.is_staff = False
            instance.is_superuser = False

        # Validação de phone (se fornecido)
        if instance.phone:
            import re

            instance.phone = re.sub(r"[^\d+\-\s()]", "", instance.phone)

        logger.debug(f"Dados validados para usuário {instance.email}")

    except Exception as e:
        logger.error(f"Erro na validação de dados do usuário: {str(e)}")


@receiver(post_save, sender=User)
def assign_user_to_group(sender, instance, created, **kwargs):
    """
    Signal para adicionar usuário ao grupo apropriado baseado no user_type.
    """
    if created:
        try:
            # Mapeia o user_type para o nome do grupo
            group_mapping = {
                "client": "Clients",
                "collaborateur": "Collaborateurs",
                "superadmin": "Super Administrateurs",
            }

            group_name = group_mapping.get(instance.user_type)

            if group_name:
                try:
                    group = Group.objects.get(name=group_name)
                    instance.groups.add(group)
                    logger.info(
                        f"Usuário {instance.email} adicionado ao grupo '{group_name}'"
                    )
                except Group.DoesNotExist:
                    logger.error(
                        f"Grupo '{group_name}' não encontrado para o usuário {instance.email}"
                    )
            else:
                logger.warning(
                    f"Tipo de usuário '{instance.user_type}' não mapeado para nenhum grupo"
                )

        except Exception as e:
            logger.error(
                f"Erro ao atribuir grupo ao usuário {instance.email}: {str(e)}"
            )


@receiver(post_save, sender=User)
def handle_user_type_change_post_save(sender, instance, created, **kwargs):
    """
    Processa mudanças no user_type após o save.
    """
    if not created and hasattr(instance, "_old_user_type"):
        if instance._old_user_type and instance._old_user_type != instance.user_type:
            try:
                # Remove dos grupos antigos
                instance.groups.clear()

                # Adiciona ao novo grupo
                group_mapping = {
                    "client": "Clients",
                    "collaborateur": "Collaborateurs",
                    "superadmin": "Super Administrateurs",
                }

                new_group_name = group_mapping.get(instance.user_type)
                if new_group_name:
                    try:
                        new_group = Group.objects.get(name=new_group_name)
                        instance.groups.add(new_group)
                        logger.info(
                            f"Usuário {instance.email} movido para o grupo '{new_group_name}'"
                        )
                    except Group.DoesNotExist:
                        logger.error(f"Grupo '{new_group_name}' não encontrado")

            except Exception as e:
                logger.error(
                    f"Erro ao atualizar grupo do usuário {instance.email}: {str(e)}"
                )


@receiver(post_save, sender=User)
def log_user_creation(sender, instance, created, **kwargs):
    """
    Signal para registrar a criação de novos usuários.
    """
    if created:
        logger.info(
            f"Novo usuário criado: {instance.email} "
            f"(Tipo: {instance.user_type}, "
            f"Ativo: {instance.is_active}, "
            f"Verificado: {instance.is_verified})"
        )


@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    """
    Envia email de boas-vindas para novos usuários.
    """
    if created and instance.is_active and not instance.is_superuser:
        try:
            from django.core.mail import send_mail
            from django.template.loader import render_to_string
            from django.conf import settings
            from django.utils.html import strip_tags

            # Prepara o contexto para o template
            context = {
                "user": instance,
                "site_name": "Lopes Peinture",
                "site_url": getattr(settings, "SITE_URL", "https://lopespeinture.fr"),
                "verification_url": f"{getattr(settings, 'SITE_URL', 'http://localhost:8000')}/accounts/verify-email/{instance.verification_token}/",
            }

            subject = f"Bienvenue chez Lopes Peinture, {instance.first_name}!"

            # Tenta renderizar templates se existirem
            try:
                html_message = render_to_string(
                    "accounts/emails/welcome_email.html", context
                )
                plain_message = strip_tags(html_message)
            except:
                # Fallback para mensagem simples
                plain_message = f"Bienvenue chez Lopes Peinture, {instance.get_full_name()}!\n\nVotre compte a été créé avec succès."
                html_message = None

            # Envia o email
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.email],
                html_message=html_message,
                fail_silently=True,
            )

            logger.info(f"Email de boas-vindas enviado para {instance.email}")

        except Exception as e:
            logger.error(
                f"Erro ao enviar email de boas-vindas para {instance.email}: {str(e)}"
            )


@receiver(post_save, sender=User)
def notify_admin_new_user(sender, instance, created, **kwargs):
    """
    Notifica administradores sobre novos usuários clientes.
    """
    if created and instance.user_type == "client":
        try:
            from django.core.mail import mail_admins

            subject = f"Nouveau client enregistré: {instance.get_full_name()}"
            message = f"""
            Un nouveau client s'est enregistré sur le système:
            
            Nom: {instance.get_full_name()}
            Email: {instance.email}
            Téléphone: {instance.phone or 'Non renseigné'}
            Date d'enregistrement: {instance.date_created.strftime('%d/%m/%Y %H:%M')}
            Statut: {'Actif' if instance.is_active else 'Inactif'}
            Email vérifié: {'Oui' if instance.is_verified else 'Non'}
            
            Accédez au panneau d'administration pour plus de détails.
            """

            mail_admins(subject=subject, message=message, fail_silently=True)

            logger.info(
                f"Notification de nouveau client envoyée aux admins: {instance.email}"
            )

        except Exception as e:
            logger.error(f"Erreur lors de la notification aux admins: {str(e)}")


@receiver(post_save, sender=User)
def log_user_status_changes(sender, instance, created, **kwargs):
    """
    Registra mudanças importantes no status do usuário para auditoria.
    """
    if not created and instance.pk:
        try:
            # Obtém a instância anterior do banco de dados
            old_instance = User.objects.get(pk=instance.pk)

            # Lista de campos importantes para monitorar
            monitored_fields = {
                "is_active": "Statut actif",
                "is_verified": "Email vérifié",
                "is_staff": "Statut staff",
                "is_superuser": "Statut super utilisateur",
                "user_type": "Type d'utilisateur",
                "email": "Email",
                "phone": "Téléphone",
                "first_name": "Prénom",
                "last_name": "Nom",
            }

            changes = []
            for field, description in monitored_fields.items():
                old_value = getattr(old_instance, field, None)
                new_value = getattr(instance, field, None)

                if old_value != new_value:
                    changes.append(f"{description}: {old_value} → {new_value}")

            if changes:
                logger.info(
                    f"Modifications utilisateur {instance.email}: {'; '.join(changes)}"
                )

        except User.DoesNotExist:
            pass  # Usuário foi deletado ou é novo
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement des modifications: {str(e)}")


@receiver(post_save, sender=User)
@receiver(pre_delete, sender=User)
def invalidate_user_cache(sender, instance, **kwargs):
    """
    Invalida cache relacionado ao usuário quando há mudanças.
    """
    try:
        # Lista de chaves de cache para invalidar
        cache_keys = [
            f"user_profile_{instance.pk}",
            f"user_permissions_{instance.pk}",
            f"user_groups_{instance.pk}",
            "users_count",
            "active_users_count",
            "verified_users_count",
            "admin_dashboard_stats",
            "clients_count",
            "collaborateurs_count",
            "superadmins_count",
        ]

        # Invalida as chaves
        cache.delete_many(cache_keys)

        # Invalida cache específico se o usuário mudou de tipo
        if (
            hasattr(instance, "_old_user_type")
            and instance._old_user_type != instance.user_type
        ):
            cache.delete_many(
                [
                    f"users_by_type_{instance._old_user_type}",
                    f"users_by_type_{instance.user_type}",
                ]
            )

        logger.debug(f"Cache invalidé pour l'utilisateur {instance.email}")

    except Exception as e:
        logger.error(f"Erreur lors de l'invalidation du cache: {str(e)}")


@receiver(pre_delete, sender=User)
def log_user_deletion(sender, instance, **kwargs):
    """
    Registra a exclusão de usuários para auditoria.
    """
    logger.warning(
        f"Utilisateur en cours de suppression: {instance.email} "
        f"(ID: {instance.pk}, Type: {instance.user_type}, "
        f"Créé le: {instance.date_created}, "
        f"Dernière connexion: {instance.last_login or 'Jamais'})"
    )


@receiver(pre_delete, sender=User)
def cleanup_user_data(sender, instance, **kwargs):
    """
    Limpa dados relacionados ao usuário antes da exclusão.
    """
    try:
        # Remove avatar se existir
        if hasattr(instance, "avatar") and instance.avatar:
            try:
                instance.avatar.delete(save=False)
                logger.info(f"Avatar supprimé pour l'utilisateur {instance.email}")
            except Exception as e:
                logger.error(f"Erreur lors de la suppression de l'avatar: {str(e)}")

        # Remove dos grupos
        instance.groups.clear()
        logger.info(f"Utilisateur {instance.email} retiré de tous les groupes")

        # Limpa permissões específicas do usuário
        instance.user_permissions.clear()
        logger.info(f"Permissions spécifiques supprimées pour {instance.email}")

        # Aqui você pode adicionar outras limpezas necessárias
        # Por exemplo: anonimizar comentários, transferir projetos, etc.

    except Exception as e:
        logger.error(f"Erreur lors du nettoyage des données: {str(e)}")


@receiver(post_save, sender=User)
def update_user_statistics(sender, instance, created, **kwargs):
    """
    Atualiza estatísticas do sistema quando usuários são criados ou modificados.
    """
    try:
        # Invalida estatísticas em cache
        cache_keys_to_delete = [
            "total_users",
            "active_users",
            "verified_users",
            "users_by_type",
            "users_created_today",
            "users_created_this_month",
            "dashboard_stats",
        ]

        cache.delete_many(cache_keys_to_delete)

        if created:
            logger.info(f"Statistiques mises à jour après création de {instance.email}")
        else:
            logger.debug(
                f"Statistiques mises à jour après modification de {instance.email}"
            )

    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour des statistiques: {str(e)}")


def create_default_superuser():
    """
    Cria um superusuário padrão se não existir nenhum.
    Útil para desenvolvimento e primeira configuração.
    """
    try:
        if not User.objects.filter(is_superuser=True).exists():
            logger.info(
                "Aucun super utilisateur trouvé. Création d'un utilisateur par défaut..."
            )

            # Só cria se estivermos em desenvolvimento
            from django.conf import settings

            if settings.DEBUG:
                User.objects.create_superuser(
                    email="admin@lopespeinture.fr",
                    first_name="Admin",
                    last_name="Lopes",
                    password="admin123",
                    user_type="superadmin",
                )
                logger.info("Super utilisateur par défaut créé: admin@lopespeinture.fr")
            else:
                logger.info(
                    "Environnement de production détecté. Super utilisateur non créé automatiquement."
                )

    except Exception as e:
        logger.error(f"Erreur lors de la création du super utilisateur: {str(e)}")


@receiver(post_migrate)
def setup_initial_data(sender, **kwargs):
    """
    Configura dados iniciais após as migrações.
    """
    if sender.name == "accounts":
        logger.info("Configuration des données initiales...")

        # Cria superusuário padrão se necessário
        create_default_superuser()

        logger.info("Configuration initiale terminée!")


# ==================== SIGNALS PARA SEGURANÇA ====================

from django.contrib.auth.signals import user_logged_in, user_login_failed


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """
    Registra logins de usuários para auditoria de segurança.
    """
    try:
        # Obtém informações da requisição
        ip_address = request.META.get(
            "HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR", "Unknown")
        )
        user_agent = request.META.get("HTTP_USER_AGENT", "Unknown")

        # Atualiza last_login_ip se o campo existir no modelo
        if hasattr(user, "last_login_ip"):
            user.last_login_ip = ip_address
            user.save(update_fields=["last_login_ip"])

        logger.info(
            f"Connexion réussie - Utilisateur: {user.email}, "
            f"IP: {ip_address}, Type: {user.user_type}"
        )

        # Limpa tentativas de login falhadas se existir o campo
        if hasattr(user, "failed_login_attempts"):
            user.failed_login_attempts = 0
            user.save(update_fields=["failed_login_attempts"])

    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement de la connexion: {str(e)}")


@receiver(user_login_failed)
def log_failed_login(sender, credentials, request, **kwargs):
    """
    Registra tentativas de login falhadas para segurança.
    """
    try:
        email = credentials.get("email", "Unknown")
        ip_address = request.META.get(
            "HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR", "Unknown")
        )

        logger.warning(
            f"Tentative de connexion échouée - Email: {email}, IP: {ip_address}"
        )

        # Incrementa contador de tentativas falhadas se o usuário existir
        try:
            user = User.objects.get(email=email)
            if hasattr(user, "failed_login_attempts"):
                user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
                user.save(update_fields=["failed_login_attempts"])

                # Bloqueia usuário após muitas tentativas
                max_attempts = getattr(settings, "MAX_FAILED_LOGIN_ATTEMPTS", 5)
                if user.failed_login_attempts >= max_attempts:
                    user.is_active = False
                    user.save(update_fields=["is_active"])
                    logger.warning(
                        f"Utilisateur {email} bloqué après {max_attempts} tentatives échouées"
                    )

        except User.DoesNotExist:
            pass  # Usuário não existe

    except Exception as e:
        logger.error(
            f"Erreur lors de l'enregistrement de l'échec de connexion: {str(e)}"
        )


# ==================== FUNÇÕES UTILITÁRIAS ====================


def reset_user_permissions():
    """
    Função utilitária para resetar todas as permissões e grupos.
    Útil para desenvolvimento e manutenção.
    """
    try:
        logger.info("Début de la réinitialisation des permissions et groupes...")

        with transaction.atomic():
            # Remove todos os usuários de todos os grupos
            for user in User.objects.all():
                user.groups.clear()
                user.user_permissions.clear()

            # Remove todos os grupos existentes
            Group.objects.all().delete()

            # Recria grupos e permissões
            setup_groups_and_permissions()

            # Reassigna usuários aos grupos baseado no user_type
            for user in User.objects.all():
                assign_user_to_group(User, user, created=False)

        logger.info("Réinitialisation des permissions terminée avec succès!")

    except Exception as e:
        logger.error(f"Erreur lors de la réinitialisation des permissions: {str(e)}")


def get_user_statistics():
    """
    Retorna estatísticas dos usuários do sistema.
    """
    try:
        stats = {
            "total_users": User.objects.count(),
            "active_users": User.objects.filter(is_active=True).count(),
            "verified_users": User.objects.filter(is_verified=True).count(),
            "clients": User.objects.filter(user_type="client").count(),
            "collaborateurs": User.objects.filter(user_type="collaborateur").count(),
            "superadmins": User.objects.filter(user_type="superadmin").count(),
            "users_today": User.objects.filter(
                date_created__date=timezone.now().date()
            ).count(),
            "users_this_month": User.objects.filter(
                date_created__year=timezone.now().year,
                date_created__month=timezone.now().month,
            ).count(),
        }

        return stats

    except Exception as e:
        logger.error(f"Erreur lors du calcul des statistiques: {str(e)}")
        return {}


def cleanup_inactive_users(days=30):
    """
    Remove usuários inativos que nunca verificaram o email após X dias.
    """
    try:
        cutoff_date = timezone.now() - timezone.timedelta(days=days)

        inactive_users = User.objects.filter(
            is_verified=False, is_active=False, date_created__lt=cutoff_date
        )

        count = inactive_users.count()

        if count > 0:
            # Log dos usuários que serão removidos
            for user in inactive_users:
                logger.info(
                    f"Suppression de l'utilisateur inactif: {user.email} "
                    f"(créé le {user.date_created})"
                )

            inactive_users.delete()
            logger.info(f"{count} utilisateurs inactifs supprimés")
        else:
            logger.info("Aucun utilisateur inactif à supprimer")

        return count

    except Exception as e:
        logger.error(f"Erreur lors du nettoyage des utilisateurs inactifs: {str(e)}")
        return 0


def send_bulk_notification(user_type=None, subject="", message="", html_message=None):
    """
    Envia notificação em massa para usuários de um tipo específico.
    """
    try:
        from django.core.mail import send_mass_mail
        from django.conf import settings

        # Filtra usuários baseado no tipo
        if user_type:
            users = User.objects.filter(
                user_type=user_type, is_active=True, is_verified=True
            )
        else:
            users = User.objects.filter(is_active=True, is_verified=True)

        if not users.exists():
            logger.warning("Aucun utilisateur trouvé pour l'envoi de notifications")
            return 0

        # Prepara as mensagens
        messages = []
        for user in users:
            personalized_message = message.replace("{name}", user.get_full_name())
            messages.append(
                (
                    subject,
                    personalized_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                )
            )

        # Envia em lotes para evitar sobrecarga
        batch_size = 50
        sent_count = 0

        for i in range(0, len(messages), batch_size):
            batch = messages[i : i + batch_size]
            try:
                send_mass_mail(batch, fail_silently=False)
                sent_count += len(batch)
                logger.info(f"Lot de {len(batch)} emails envoyé")
            except Exception as e:
                logger.error(f"Erreur lors de l'envoi du lot: {str(e)}")

        logger.info(f"Notification envoyée à {sent_count} utilisateurs")
        return sent_count

    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de notifications en masse: {str(e)}")
        return 0


def export_users_data(user_type=None, format="csv"):
    """
    Exporta dados dos usuários em formato CSV ou JSON.
    """
    try:
        import csv
        import json
        from io import StringIO
        from django.utils import timezone

        # Filtra usuários
        if user_type:
            users = User.objects.filter(user_type=user_type)
        else:
            users = User.objects.all()

        if format.lower() == "csv":
            output = StringIO()
            writer = csv.writer(output)

            # Cabeçalho
            writer.writerow(
                [
                    "Email",
                    "Prénom",
                    "Nom",
                    "Téléphone",
                    "Type",
                    "Actif",
                    "Vérifié",
                    "Date de création",
                    "Dernière connexion",
                ]
            )

            # Dados
            for user in users:
                writer.writerow(
                    [
                        user.email,
                        user.first_name,
                        user.last_name,
                        user.phone or "",
                        user.user_type,
                        "Oui" if user.is_active else "Non",
                        "Oui" if user.is_verified else "Non",
                        user.date_created.strftime("%d/%m/%Y %H:%M"),
                        (
                            user.last_login.strftime("%d/%m/%Y %H:%M")
                            if user.last_login
                            else "Jamais"
                        ),
                    ]
                )

            return output.getvalue()

        elif format.lower() == "json":
            data = []
            for user in users:
                data.append(
                    {
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "phone": user.phone,
                        "user_type": user.user_type,
                        "is_active": user.is_active,
                        "is_verified": user.is_verified,
                        "date_created": user.date_created.isoformat(),
                        "last_login": (
                            user.last_login.isoformat() if user.last_login else None
                        ),
                    }
                )

            return json.dumps(data, indent=2, ensure_ascii=False)

    except Exception as e:
        logger.error(f"Erreur lors de l'export des données: {str(e)}")
        return None


def validate_user_data_integrity():
    """
    Valida a integridade dos dados dos usuários e corrige inconsistências.
    """
    try:
        logger.info("Début de la validation de l'intégrité des données...")

        issues_found = 0
        issues_fixed = 0

        # Verifica usuários sem email
        users_without_email = User.objects.filter(email__isnull=True)
        if users_without_email.exists():
            logger.warning(
                f"{users_without_email.count()} utilisateurs sans email trouvés"
            )
            issues_found += users_without_email.count()

        # Verifica superadmins que não são staff
        invalid_superadmins = User.objects.filter(
            user_type="superadmin", is_staff=False
        )
        if invalid_superadmins.exists():
            invalid_superadmins.update(is_staff=True)
            logger.info(
                f"{invalid_superadmins.count()} superadmins corrigés (is_staff=True)"
            )
            issues_fixed += invalid_superadmins.count()

        # Verifica clientes que são staff
        invalid_clients = User.objects.filter(user_type="client", is_staff=True)
        if invalid_clients.exists():
            invalid_clients.update(is_staff=False, is_superuser=False)
            logger.info(f"{invalid_clients.count()} clients corrigés (is_staff=False)")
            issues_fixed += invalid_clients.count()

        # Verifica usuários sem grupos apropriados
        users_without_groups = User.objects.filter(groups__isnull=True)
        for user in users_without_groups:
            assign_user_to_group(User, user, created=False)
            issues_fixed += 1

        logger.info(
            f"Validation terminée: {issues_found} problèmes trouvés, "
            f"{issues_fixed} problèmes corrigés"
        )

        return {"issues_found": issues_found, "issues_fixed": issues_fixed}

    except Exception as e:
        logger.error(f"Erreur lors de la validation de l'intégrité: {str(e)}")
        return {"issues_found": 0, "issues_fixed": 0}


# ==================== CONFIGURAÇÃO DE LOGGING ESPECÍFICO ====================

# Configura logger específico para signals se não existir
if not logger.handlers:
    import sys

    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(
        logging.Formatter(
            "[%(asctime)s] %(levelname)s [accounts.signals] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    # Handler para arquivo (se em produção)
    try:
        from django.conf import settings

        if hasattr(settings, "LOGGING") and not settings.DEBUG:
            file_handler = logging.FileHandler("logs/accounts_signals.log")
            file_handler.setFormatter(
                logging.Formatter(
                    "[%(asctime)s] %(levelname)s [%(name)s] %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                )
            )
            logger.addHandler(file_handler)
    except:
        pass  # Se não conseguir configurar arquivo, usa apenas console

    logger.addHandler(console_handler)
    logger.setLevel(logging.INFO)


# ==================== SIGNAL PARA CACHE ====================


@receiver(post_save, sender=User)
def update_cache_on_user_change(sender, instance, created, **kwargs):
    """
    Atualiza cache específico quando usuário é modificado.
    """
    try:
        # Chaves de cache específicas do usuário
        user_cache_keys = [
            f"user_{instance.pk}",
            f"user_profile_{instance.pk}",
            f"user_permissions_{instance.pk}",
            f"user_groups_{instance.pk}",
        ]

        # Chaves de cache globais
        global_cache_keys = [
            "all_users",
            "active_users_list",
            "user_statistics",
            f"users_by_type_{instance.user_type}",
        ]

        # Remove cache global
        cache.delete_many(global_cache_keys)

        # Se o usuário mudou de tipo, limpa cache do tipo anterior também
        if (
            hasattr(instance, "_old_user_type")
            and instance._old_user_type != instance.user_type
        ):
            cache.delete(f"users_by_type_{instance._old_user_type}")

        logger.debug(f"Cache mis à jour pour l'utilisateur {instance.email}")

    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du cache: {str(e)}")


# ==================== SIGNAL PARA BACKUP AUTOMÁTICO ====================


@receiver(pre_delete, sender=User)
def backup_user_before_deletion(sender, instance, **kwargs):
    """
    Cria backup dos dados do usuário antes da exclusão.
    """
    try:
        import json
        from django.conf import settings
        from pathlib import Path

        # Cria diretório de backup se não existir
        backup_dir = Path(settings.BASE_DIR) / "backups" / "users"
        backup_dir.mkdir(parents=True, exist_ok=True)

        # Dados do usuário para backup
        user_data = {
            "id": instance.pk,
            "email": instance.email,
            "first_name": instance.first_name,
            "last_name": instance.last_name,
            "phone": instance.phone,
            "user_type": instance.user_type,
            "is_active": instance.is_active,
            "is_verified": instance.is_verified,
            "is_staff": instance.is_staff,
            "is_superuser": instance.is_superuser,
            "date_created": instance.date_created.isoformat(),
            "date_updated": (
                instance.date_updated.isoformat()
                if hasattr(instance, "date_updated")
                else None
            ),
            "last_login": (
                instance.last_login.isoformat() if instance.last_login else None
            ),
            "groups": list(instance.groups.values_list("name", flat=True)),
            "permissions": list(
                instance.user_permissions.values_list("codename", flat=True)
            ),
            "deletion_date": timezone.now().isoformat(),
        }

        # Nome do arquivo de backup
        backup_filename = f"user_{instance.pk}_{instance.email}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.json"
        backup_path = backup_dir / backup_filename

        # Salva o backup
        with open(backup_path, "w", encoding="utf-8") as f:
            json.dump(user_data, f, indent=2, ensure_ascii=False)

        logger.info(
            f"Backup créé pour l'utilisateur {instance.email}: {backup_filename}"
        )

    except Exception as e:
        logger.error(f"Erreur lors de la création du backup: {str(e)}")


# ==================== SIGNALS PARA MONITORAMENTO ====================


@receiver(post_save, sender=User)
def monitor_suspicious_activity(sender, instance, created, **kwargs):
    """
    Monitora atividades suspeitas nos usuários.
    """
    try:
        # Verifica mudanças suspeitas apenas em usuários existentes
        if not created and instance.pk:
            try:
                old_instance = User.objects.get(pk=instance.pk)

                # Flags de atividade suspeita
                suspicious_flags = []

                # Mudança de email
                if old_instance.email != instance.email:
                    suspicious_flags.append(
                        f"Email changé: {old_instance.email} → {instance.email}"
                    )

                # Mudança de tipo de usuário
                if old_instance.user_type != instance.user_type:
                    suspicious_flags.append(
                        f"Type changé: {old_instance.user_type} → {instance.user_type}"
                    )

                # Elevação de privilégios
                if not old_instance.is_superuser and instance.is_superuser:
                    suspicious_flags.append("Privilèges super utilisateur accordés")

                if not old_instance.is_staff and instance.is_staff:
                    suspicious_flags.append("Privilèges staff accordés")

                # Reativação de conta inativa
                if not old_instance.is_active and instance.is_active:
                    suspicious_flags.append("Compte réactivé")

                # Log atividades suspeitas
                if suspicious_flags:
                    logger.warning(
                        f"Activité suspecte détectée pour {instance.email}: "
                        f"{'; '.join(suspicious_flags)}"
                    )

                    # Aqui você pode adicionar notificações para admins
                    # ou outras medidas de segurança

            except User.DoesNotExist:
                pass  # Usuário foi deletado

    except Exception as e:
        logger.error(f"Erreur lors du monitoring de sécurité: {str(e)}")


# ==================== SIGNALS PARA MÉTRICAS ====================


@receiver(post_save, sender=User)
@receiver(pre_delete, sender=User)
def update_system_metrics(sender, instance, **kwargs):
    """
    Atualiza métricas do sistema quando usuários são modificados.
    """
    try:
        from django.core.cache import cache

        # Chaves de métricas para invalidar
        metrics_keys = [
            "metrics_total_users",
            "metrics_active_users",
            "metrics_verified_users",
            "metrics_users_by_type",
            "metrics_users_created_today",
            "metrics_users_created_this_week",
            "metrics_users_created_this_month",
            "metrics_login_activity",
            "dashboard_metrics",
        ]

        cache.delete_many(metrics_keys)

        # Força recálculo das métricas principais
        try:
            current_metrics = {
                "total_users": User.objects.count(),
                "active_users": User.objects.filter(is_active=True).count(),
                "verified_users": User.objects.filter(is_verified=True).count(),
                "timestamp": timezone.now().isoformat(),
            }

            cache.set("current_user_metrics", current_metrics, timeout=300)  # 5 minutos

        except Exception as e:
            logger.error(f"Erreur lors du calcul des métriques: {str(e)}")

    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour des métriques: {str(e)}")


# ==================== SIGNAL PARA LIMPEZA AUTOMÁTICA ====================


@receiver(post_migrate)
def schedule_cleanup_tasks(sender, **kwargs):
    """
    Agenda tarefas de limpeza automática após migrações.
    """
    if sender.name == "accounts":
        try:
            # Aqui você pode agendar tarefas de limpeza
            # Por exemplo, usando Celery ou Django-Q

            logger.info("Tâches de nettoyage programmées")

            # Exemplo de limpeza imediata de dados órfãos
            cleanup_orphaned_data()

        except Exception as e:
            logger.error(f"Erreur lors de la programmation des tâches: {str(e)}")


def cleanup_orphaned_data():
    """
    Limpa dados órfãos do sistema.
    """
    try:
        # Remove grupos vazios (exceto os padrão)
        default_groups = ["Clients", "Collaborateurs", "Super Administrateurs"]
        empty_groups = Group.objects.exclude(name__in=default_groups).filter(user=None)

        if empty_groups.exists():
            count = empty_groups.count()
            empty_groups.delete()
            logger.info(f"{count} groupes vides supprimés")

        # Limpa cache expirado relacionado a usuários
        cache_patterns = ["user_*", "users_*", "metrics_*", "dashboard_*"]

        # Note: Django cache não suporta wildcard delete nativamente
        # Você pode implementar isso com Redis ou Memcached específicos

        logger.info("Nettoyage des données orphelines terminé")

    except Exception as e:
        logger.error(f"Erreur lors du nettoyage des données orphelines: {str(e)}")


# ==================== SIGNAL PARA VALIDAÇÃO DE INTEGRIDADE ====================


@receiver(post_save, sender=User)
def validate_user_integrity(sender, instance, created, **kwargs):
    """
    Valida a integridade dos dados do usuário após salvamento.
    """
    try:
        integrity_issues = []

        # Validações básicas
        if not instance.email:
            integrity_issues.append("Email manquant")

        if not instance.first_name:
            integrity_issues.append("Prénom manquant")

        if not instance.last_name:
            integrity_issues.append("Nom manquant")

        # Validações específicas por tipo de usuário
        if instance.user_type == "superadmin":
            if not instance.is_staff:
                instance.is_staff = True
                instance.save(update_fields=["is_staff"])
                logger.info(
                    f"Correction automatique: is_staff défini pour {instance.email}"
                )

        elif instance.user_type == "client":
            if instance.is_staff or instance.is_superuser:
                instance.is_staff = False
                instance.is_superuser = False
                instance.save(update_fields=["is_staff", "is_superuser"])
                logger.info(
                    f"Correction automatique: privilèges retirés pour le client {instance.email}"
                )

        # Validação de grupos
        expected_group = {
            "client": "Clients",
            "collaborateur": "Collaborateurs",
            "superadmin": "Super Administrateurs",
        }.get(instance.user_type)

        if expected_group:
            try:
                group = Group.objects.get(name=expected_group)
                if not instance.groups.filter(name=expected_group).exists():
                    instance.groups.add(group)
                    logger.info(
                        f"Utilisateur {instance.email} ajouté au groupe {expected_group}"
                    )
            except Group.DoesNotExist:
                integrity_issues.append(f"Groupe {expected_group} manquant")

        # Log problemas de integridade
        if integrity_issues:
            logger.warning(
                f"Problèmes d'intégrité détectés pour {instance.email}: "
                f"{'; '.join(integrity_issues)}"
            )

    except Exception as e:
        logger.error(f"Erreur lors de la validation d'intégrité: {str(e)}")


# ==================== CONFIGURAÇÃO FINAL ====================

# Garante que o logger está configurado corretamente
logger.info("Signals do módulo accounts carregados com sucesso")

# Exporta funções utilitárias para uso externo
__all__ = [
    "setup_groups_and_permissions",
    "reset_user_permissions",
    "get_user_statistics",
    "cleanup_inactive_users",
    "send_bulk_notification",
    "export_users_data",
    "validate_user_data_integrity",
]
