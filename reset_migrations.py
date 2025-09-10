"""
Script para resetar migrações em desenvolvimento.
ATENÇÃO: Só use em desenvolvimento! Vai apagar todos os dados!
"""

import os
import glob
import sqlite3


def reset_migrations():
    """
    Reseta completamente as migrações e banco de dados.
    """
    print("🚨 ATENÇÃO: Este script vai APAGAR TODOS OS DADOS!")
    print("💾 Só use em desenvolvimento!")

    confirm = input("🤔 Tem certeza? Digite 'CONFIRMO' para prosseguir: ")

    if confirm != "CONFIRMO":
        print("❌ Operação cancelada.")
        return

    print("\n🔧 Iniciando reset das migrações...")

    # 1. Deletar banco de dados
    if os.path.exists("db.sqlite3"):
        os.remove("db.sqlite3")
        print("✅ Banco de dados deletado")

    # 2. Deletar arquivos de migração (exceto __init__.py)
    apps_with_migrations = ["accounts", "profiles", "projects"]

    for app in apps_with_migrations:
        migrations_dir = f"{app}/migrations"
        if os.path.exists(migrations_dir):
            # Buscar arquivos de migração
            migration_files = glob.glob(f"{migrations_dir}/[0-9]*.py")

            for file in migration_files:
                os.remove(file)
                print(f"✅ Deletado: {file}")

            # Deletar __pycache__
            pycache_dir = f"{migrations_dir}/__pycache__"
            if os.path.exists(pycache_dir):
                import shutil

                shutil.rmtree(pycache_dir)
                print(f"✅ Cache deletado: {pycache_dir}")

    print("\n🔧 Reset concluído!")
    print("🚀 Agora execute:")
    print("   python manage.py makemigrations")
    print("   python manage.py migrate")
    print("   python manage.py createsuperuser")


if __name__ == "__main__":
    reset_migrations()
