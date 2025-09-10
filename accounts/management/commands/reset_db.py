import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.management import call_command


class Command(BaseCommand):
    """
    Comando para resetar o banco de dados
    Usage: python manage.py reset_db
    """

    help = "Reseta o banco de dados e recria tudo do zero"

    def add_arguments(self, parser):
        parser.add_argument(
            "--confirm", action="store_true", help="Confirma o reset sem perguntar"
        )

    def handle(self, *args, **options):
        if not options["confirm"]:
            confirm = input(
                '⚠️  ATENÇÃO: Isso vai DELETAR todos os dados! Continuar? (digite "CONFIRMO"): '
            )
            if confirm != "CONFIRMO":
                self.stdout.write("❌ Operação cancelada")
                return

        self.stdout.write(self.style.WARNING("🔄 RESETANDO BANCO DE DADOS..."))

        # 1. Deletar arquivo do banco SQLite
        db_path = settings.DATABASES["default"]["NAME"]
        if os.path.exists(db_path):
            os.remove(db_path)
            self.stdout.write(f"✅ Banco deletado: {db_path}")

        # 2. Deletar arquivos de migração
        apps_with_migrations = ["accounts", "profiles"]
        for app in apps_with_migrations:
            migrations_dir = os.path.join(app, "migrations")
            if os.path.exists(migrations_dir):
                for filename in os.listdir(migrations_dir):
                    if filename.startswith("0") and filename.endswith(".py"):
                        file_path = os.path.join(migrations_dir, filename)
                        os.remove(file_path)
                        self.stdout.write(f"✅ Migração deletada: {file_path}")

        # 3. Recriar migrações e aplicar
        self.stdout.write("🔄 Recriando migrações...")
        call_command("makemigrations")
        call_command("migrate")

        # 4. Executar setup
        self.stdout.write("🔄 Executando setup inicial...")
        call_command(
            "setup_site",
            "--admin-email=admin@lopespeinture.com",
            "--admin-password=admin123",
        )

        self.stdout.write(
            self.style.SUCCESS("✅ RESET CONCLUÍDO! Banco recriado do zero.")
        )
