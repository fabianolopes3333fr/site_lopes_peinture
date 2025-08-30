from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import transaction
import getpass

User = get_user_model()


class Command(BaseCommand):
    help = "Criar um superusuário com perfil completo"

    def add_arguments(self, parser):
        parser.add_argument(
            "--email",
            type=str,
            help="Email do superusuário",
        )
        parser.add_argument(
            "--first-name",
            type=str,
            help="Prénom do superusuário",
        )
        parser.add_argument(
            "--last-name",
            type=str,
            help="Nom do superusuário",
        )
        parser.add_argument(
            "--phone",
            type=str,
            help="Téléphone do superusuário",
        )
        parser.add_argument(
            "--no-input",
            action="store_true",
            help="Não solicitar entrada do usuário",
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("=== Création d'un Super Administrateur ===\n")
        )

        # Verificar se já existe um superuser
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write(
                self.style.WARNING("⚠️  Un super administrateur existe déjà.")
            )
            confirm = input("Voulez-vous créer un autre super administrateur ? (o/N): ")
            if confirm.lower() not in ["o", "oui", "y", "yes"]:
                self.stdout.write(self.style.ERROR("Opération annulée."))
                return

        try:
            with transaction.atomic():
                # Coletar dados
                email = self._get_email(options)
                first_name = self._get_first_name(options)
                last_name = self._get_last_name(options)
                phone = self._get_phone(options)
                password = self._get_password(options)

                # Criar o usuário
                user = User.objects.create_user(
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    phone=phone,
                    password=password,
                    user_type="superadmin",
                    is_staff=True,
                    is_superuser=True,
                    is_verified=True,
                )

                # Criar grupos se não existirem
                admin_group, created = Group.objects.get_or_create(
                    name="Administrateurs"
                )
                if created:
                    self.stdout.write(
                        self.style.SUCCESS('✅ Groupe "Administrateurs" créé.')
                    )

                # Adicionar ao grupo de administradores
                user.groups.add(admin_group)

                self.stdout.write(
                    self.style.SUCCESS(f"\n✅ Super administrateur créé avec succès!")
                )
                self.stdout.write(f"📧 Email: {email}")
                self.stdout.write(f"👤 Nom: {first_name} {last_name}")
                self.stdout.write(f'📱 Téléphone: {phone or "Non renseigné"}')
                self.stdout.write(f"🔑 Type: Super Administrateur")
                self.stdout.write(f"👥 Groupe: Administrateurs")

                self.stdout.write(
                    self.style.WARNING(f"\n⚠️  Conservez ces informations en sécurité!")
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Erreur lors de la création: {str(e)}")
            )

    def _get_email(self, options):
        """Obter email do superuser"""
        email = options.get("email")

        while not email:
            email = input("📧 Email du super administrateur: ").strip()
            if not email:
                self.stdout.write(self.style.ERROR("L'email est obligatoire."))
                continue

            # Verificar se já existe
            if User.objects.filter(email=email.lower()).exists():
                self.stdout.write(
                    self.style.ERROR(
                        f'❌ Un utilisateur avec l\'email "{email}" existe déjà.'
                    )
                )
                email = None
                continue

            # Validação básica de email
            if "@" not in email or "." not in email:
                self.stdout.write(self.style.ERROR("Format d'email invalide."))
                email = None
                continue

        return email.lower()

    def _get_first_name(self, options):
        """Obter primeiro nome"""
        first_name = options.get("first_name")

        while not first_name:
            first_name = input("👤 Prénom: ").strip()
            if not first_name:
                self.stdout.write(self.style.ERROR("Le prénom est obligatoire."))

        return first_name

    def _get_last_name(self, options):
        """Obter sobrenome"""
        last_name = options.get("last_name")

        while not last_name:
            last_name = input("👤 Nom: ").strip()
            if not last_name:
                self.stdout.write(self.style.ERROR("Le nom est obligatoire."))

        return last_name

    def _get_phone(self, options):
        """Obter telefone (opcional)"""
        phone = options.get("phone")

        if not phone and not options.get("no_input"):
            phone = input("📱 Téléphone (optionnel): ").strip()

        return phone or None

    def _get_password(self, options):
        """Obter senha"""
        if options.get("no_input"):
            return "admin123"  # Senha padrão para modo não interativo

        while True:
            password = getpass.getpass("🔑 Mot de passe: ")
            if len(password) < 8:
                self.stdout.write(
                    self.style.ERROR(
                        "Le mot de passe doit contenir au moins 8 caractères."
                    )
                )
                continue

            password2 = getpass.getpass("🔑 Confirmez le mot de passe: ")
            if password != password2:
                self.stdout.write(
                    self.style.ERROR("Les mots de passe ne correspondent pas.")
                )
                continue

            return password
