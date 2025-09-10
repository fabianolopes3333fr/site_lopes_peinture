from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from profiles.models import Profile

User = get_user_model()


class Command(BaseCommand):
    """
    Comando para criar usuários de teste
    Usage: python manage.py create_test_users
    """

    help = "Cria usuários de teste para desenvolvimento"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=5,
            help="Número de usuários de cada tipo para criar (padrão: 5)",
        )
        parser.add_argument(
            "--password",
            type=str,
            default="test123",
            help="Senha para todos os usuários de teste (padrão: test123)",
        )

    def handle(self, *args, **options):
        count = options["count"]
        password = options["password"]

        self.stdout.write(self.style.SUCCESS("🧪 CRIANDO USUÁRIOS DE TESTE"))
        self.stdout.write("=" * 50)

        # Dados de teste
        test_users = [
            # Clientes
            {
                "type": "CLIENT",
                "users": [
                    ("jean.dupont@email.com", "Jean", "Dupont"),
                    ("marie.martin@email.com", "Marie", "Martin"),
                    ("pierre.durand@email.com", "Pierre", "Durand"),
                    ("sophie.leroy@email.com", "Sophie", "Leroy"),
                    ("michel.bernard@email.com", "Michel", "Bernard"),
                ],
            },
            # Colaboradores
            {
                "type": "COLLABORATOR",
                "users": [
                    ("paul.peintre@lopespeinture.com", "Paul", "Peintre"),
                    ("ana.assistante@lopespeinture.com", "Ana", "Assistante"),
                    ("carlos.chef@lopespeinture.com", "Carlos", "Chef"),
                    ("lucia.decoratrice@lopespeinture.com", "Lucia", "Décoratrice"),
                    ("rui.technicien@lopespeinture.com", "Rui", "Technicien"),
                ],
            },
        ]

        for user_type_data in test_users:
            account_type = user_type_data["type"]
            users_data = user_type_data["users"][:count]

            self.stdout.write(f"\n👤 Criando {account_type}S...")

            for email, first_name, last_name in users_data:
                try:
                    # Verificar se já existe
                    if User.objects.filter(email=email).exists():
                        self.stdout.write(f"  ⏭️  Já existe: {email}")
                        continue

                    # Criar usuário
                    user = User.objects.create_user(
                        email=email,
                        password=password,
                        first_name=first_name,
                        last_name=last_name,
                        account_type=account_type,
                    )

                    # Perfil será criado automaticamente via signals

                    # Verificar se perfil foi criado
                    if hasattr(user, "profile"):
                        # Adicionar dados de teste ao perfil
                        profile = user.profile
                        profile.phone = "+33 1 23 45 67 89"
                        profile.address = f"{first_name} Street, 123"
                        profile.city = "Paris"
                        profile.postal_code = "75001"
                        profile.country = "France"
                        profile.save()

                    self.stdout.write(
                        f"  ✅ Criado: {email} ({first_name} {last_name})"
                    )

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"  ❌ Erro ao criar {email}: {e}")
                    )

        # Estatísticas finais
        self.stdout.write("\n📊 ESTATÍSTICAS:")
        clients = User.objects.filter(account_type="CLIENT").count()
        collaborators = User.objects.filter(account_type="COLLABORATOR").count()
        admins = User.objects.filter(account_type="ADMINISTRATOR").count()

        self.stdout.write(f"  👥 Clientes: {clients}")
        self.stdout.write(f"  🤝 Colaboradores: {collaborators}")
        self.stdout.write(f"  👑 Administradores: {admins}")
        self.stdout.write(f"  📝 Total: {User.objects.count()}")

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ Usuários de teste criados! Senha para todos: {password}"
            )
        )
