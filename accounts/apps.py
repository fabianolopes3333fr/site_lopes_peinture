from django.apps import AppConfig
from django.db.models.signals import post_migrate


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    verbose_name = 'Comptes Utilisateurs'

    def ready(self):
        """
        Método chamado quando a aplicação está pronta.
        Registra os signals e configurações iniciais.
        """
        try:
            # Importar signals
            import accounts.signals
            
            # Registrar função para configurar grupos após migração
            post_migrate.connect(setup_groups_and_permissions, sender=self)
            
        except ImportError:
            pass


def setup_groups_and_permissions(sender, **kwargs):
    """
    Configura grupos e permissões após as migrações.
    
    Args:
        sender: A aplicação que enviou o signal
        **kwargs: Argumentos adicionais do signal
    """
    from django.contrib.auth.models import Group, Permission
    from django.contrib.contenttypes.models import ContentType
    from accounts.models import User
    
    # Criar grupos se não existirem
    groups_permissions = {
        'Clients': [
            'view_user',  # Ver próprio perfil
        ],
        'Collaborateurs': [
            'view_user',
            'change_user',  # Editar perfis de clientes
            'add_user',     # Adicionar novos usuários
        ],
        'Super Admins': [
            'view_user',
            'add_user',
            'change_user',
            'delete_user',
        ]
    }
    
    try:
        user_content_type = ContentType.objects.get_for_model(User)
        
        for group_name, permissions in groups_permissions.items():
            group, created = Group.objects.get_or_create(name=group_name)
            
            if created:
                print(f"✓ Grupo '{group_name}' criado com sucesso")
            
            # Adicionar permissões ao grupo
            for perm_codename in permissions:
                try:
                    permission = Permission.objects.get(
                        codename=perm_codename,
                        content_type=user_content_type
                    )
                    group.permissions.add(permission)
                except Permission.DoesNotExist:
                    print(f"⚠️ Permissão '{perm_codename}' não encontrada")
            
            if created:
                print(f"✓ Permissões adicionadas ao grupo '{group_name}'")
                
    except Exception as e:
        print(f"❌ Erro ao configurar grupos: {e}")