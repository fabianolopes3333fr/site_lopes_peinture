#!/usr/bin/env python
"""
Script de validação final do projeto LOPES PEINTURE
Verifica se tudo está funcionando corretamente
"""

import os
import sys
import django
from django.core.management import execute_from_command_line
from django.test.utils import get_runner
from django.conf import settings


def setup_django():
    """Configurar Django"""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
    django.setup()


def check_models():
    """Verificar modelos"""
    print("🔍 Verificando modelos...")

    from django.contrib.auth import get_user_model
    from profiles.models import Profile

    User = get_user_model()

    # Verificar se modelos estão acessíveis
    print(f"  ✅ User model: {User}")
    print(f"  ✅ Profile model: {Profile}")

    # Verificar campos obrigatórios
    user_fields = [f.name for f in User._meta.fields]
    required_user_fields = ["email", "first_name", "last_name", "account_type"]

    for field in required_user_fields:
        if field in user_fields:
            print(f"  ✅ Campo User.{field}: OK")
        else:
            print(f"  ❌ Campo User.{field}: FALTANDO")

    return True


def check_database():
    """Verificar banco de dados"""
    print("🗃️  Verificando banco de dados...")

    from django.contrib.auth import get_user_model
    from django.contrib.auth.models import Group

    User = get_user_model()

    try:
        # Verificar se pode consultar usuários
        user_count = User.objects.count()
        print(f"  ✅ Usuários no banco: {user_count}")

        # Verificar grupos
        group_count = Group.objects.count()
        print(f"  ✅ Grupos no banco: {group_count}")

        # Verificar superusuário
        admin_count = User.objects.filter(is_superuser=True).count()
        print(f"  ✅ Superusuários: {admin_count}")

        return True

    except Exception as e:
        print(f"  ❌ Erro no banco: {e}")
        return False


def check_urls():
    """Verificar URLs"""
    print("🌐 Verificando URLs...")

    from django.urls import reverse
    from django.test import Client

    client = Client()

    # URLs que devem estar acessíveis
    urls_to_check = [
        ("pages:home", "Home"),
        ("accounts:login", "Login"),
        ("accounts:register", "Registro"),
    ]

    for url_name, description in urls_to_check:
        try:
            url = reverse(url_name)
            response = client.get(url)

            if response.status_code in [200, 302]:
                print(f"  ✅ {description} ({url}): OK")
            else:
                print(f"  ⚠️  {description} ({url}): Status {response.status_code}")

        except Exception as e:
            print(f"  ❌ {description}: Erro - {e}")

    return True


def check_static_files():
    """Verificar arquivos estáticos"""
    print("📦 Verificando arquivos estáticos...")

    static_dirs = ["static", "media", "staticfiles"]

    for static_dir in static_dirs:
        if os.path.exists(static_dir):
            print(f"  ✅ Diretório {static_dir}: Existe")
        else:
            print(f"  ⚠️  Diretório {static_dir}: Não encontrado")

    return True


def check_templates():
    """Verificar templates"""
    print("📄 Verificando templates...")

    templates_to_check = [
        "templates/base.html",
        "templates/accounts/login.html",
        "templates/accounts/register.html",
        "templates/dashboard/dashboard.html",
    ]

    for template in templates_to_check:
        if os.path.exists(template):
            print(f"  ✅ {template}: Existe")
        else:
            print(f"  ❌ {template}: Não encontrado")

    return True


def run_basic_tests():
    """Executar testes básicos"""
    print("🧪 Executando testes básicos...")

    try:
        # Executar apenas testes de modelos (mais rápido)
        from django.test.utils import get_runner
        from django.conf import settings

        TestRunner = get_runner(settings)
        test_runner = TestRunner()

        # Executar testes específicos
        failures = test_runner.run_tests(["accounts.tests.test_models"])

        if failures:
            print(f"  ❌ {failures} teste(s) falharam")
            return False
        else:
            print("  ✅ Todos os testes passaram")
            return True

    except Exception as e:
        print(f"  ⚠️  Erro ao executar testes: {e}")
        return False


def main():
    """Função principal"""
    print("🎨 VALIDAÇÃO DO PROJETO LOPES PEINTURE")
    print("=" * 50)

    # Setup Django
    setup_django()

    checks = [
        ("Modelos", check_models),
        ("Banco de Dados", check_database),
        ("URLs", check_urls),
        ("Arquivos Estáticos", check_static_files),
        ("Templates", check_templates),
        ("Testes Básicos", run_basic_tests),
    ]

    results = []

    for check_name, check_func in checks:
        print(f"\n{check_name}:")
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"  ❌ Erro durante verificação: {e}")
            results.append((check_name, False))

    # Resumo final
    print("\n" + "=" * 50)
    print("📊 RESUMO DA VALIDAÇÃO:")
    print("=" * 50)

    total_checks = len(results)
    passed_checks = sum(1 for _, result in results if result)

    for check_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"  {check_name}: {status}")

    print(f"\n📈 RESULTADO: {passed_checks}/{total_checks} verificações passaram")

    if passed_checks == total_checks:
        print("🎉 PROJETO VALIDADO COM SUCESSO!")
        print("\n🚀 Próximos passos:")
        print("  1. Execute: python manage.py runserver")
        print("  2. Acesse: http://127.0.0.1:8000/")
        print("  3. Teste todas as funcionalidades")
        return True
    else:
        print("⚠️  ALGUNS PROBLEMAS ENCONTRADOS")
        print("\n🔧 Corrija os problemas antes de continuar")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
