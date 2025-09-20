"""
Script para diagnosticar problemas na criação de produtos
Execute: python manage.py shell < diagnose_product_issues.py
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.urls import reverse
from django.test import Client
from django.contrib.auth import get_user_model
from projects.models import Product
from projects.forms import ProduitForm
from accounts.models import AccountType

User = get_user_model()


def diagnose_product_creation():
    """Diagnóstico completo dos problemas de criação de produtos"""

    print("🔍 DIAGNÓSTICO DE PROBLEMAS NA CRIAÇÃO DE PRODUTOS")
    print("=" * 60)

    # 1. Verificar imports
    print("\n1. Verificando imports...")
    try:
        from projects.models import Product, ProductType, Unit
        from projects.forms import ProduitForm
        from projects.views import produit_create

        print("   ✅ Todos os imports funcionando")
    except ImportError as e:
        print(f"   ❌ Erro de import: {e}")
        return

    # 2. Verificar modelo Product
    print("\n2. Verificando modelo Product...")
    try:
        fields = [f.name for f in Product._meta.fields]
        print(f"   ✅ Campos do modelo: {fields}")

        # Verificar choices
        print(f"   ✅ ProductType choices: {len(ProductType.choices)} opções")
        print(f"   ✅ Unit choices: {len(Unit.choices)} opções")

    except Exception as e:
        print(f"   ❌ Erro no modelo: {e}")

    # 3. Verificar formulário
    print("\n3. Verificando formulário...")
    try:
        form = ProduitForm()
        form_fields = list(form.fields.keys())
        model_fields = [f.name for f in Product._meta.fields]

        print(f"   ✅ Campos do formulário: {form_fields}")

        # Verificar se todos os campos do form existem no modelo
        for field in form_fields:
            if field in model_fields:
                print(f"   ✅ Campo {field}: OK")
            else:
                print(f"   ❌ Campo {field}: NÃO EXISTE NO MODELO")

    except Exception as e:
        print(f"   ❌ Erro no formulário: {e}")

    # 4. Verificar URLs
    print("\n4. Verificando URLs...")
    try:
        create_url = reverse("projects:produit_create")
        list_url = reverse("projects:produit_list")
        print(f"   ✅ URL create: {create_url}")
        print(f"   ✅ URL list: {list_url}")
    except Exception as e:
        print(f"   ❌ Erro nas URLs: {e}")

    # 5. Verificar permissões
    print("\n5. Verificando sistema de permissões...")
    try:
        from projects.views import can_access_products_devis

        # Criar usuário teste
        admin = User.objects.create_user(
            username="diag_admin",
            email="diag@admin.com",
            password="test123",
            is_staff=True,
            account_type=AccountType.ADMINISTRATOR,
        )

        permission = can_access_products_devis(admin)
        print(f"   ✅ Permissão admin: {permission}")

        # Limpar usuário teste
        admin.delete()

    except Exception as e:
        print(f"   ❌ Erro nas permissões: {e}")

    # 6. Teste de criação via ORM
    print("\n6. Testando criação via ORM...")
    try:
        product = Product.objects.create(
            code="DIAG-001",
            name="Produto Diagnóstico",
            description="Teste de diagnóstico",
            type_produit=ProductType.PAINT,
            price_unit=25.00,
            unit=Unit.LITER,
            is_active=True,
        )
        print(f"   ✅ Produto criado: {product}")

        # Limpar
        product.delete()

    except Exception as e:
        print(f"   ❌ Erro na criação ORM: {e}")

    # 7. Teste do formulário com dados
    print("\n7. Testando formulário com dados...")
    try:
        form_data = {
            "code": "DIAG-FORM-001",
            "name": "Produto Formulário Diagnóstico",
            "description": "Teste formulário",
            "type_produit": ProductType.PAINT,
            "price_unit": "30.00",
            "unit": Unit.M2,
            "is_active": True,
        }

        form = ProduitForm(data=form_data)
        if form.is_valid():
            product = form.save()
            print(f"   ✅ Produto via formulário: {product}")
            product.delete()
        else:
            print(f"   ❌ Formulário inválido: {form.errors}")

    except Exception as e:
        print(f"   ❌ Erro no teste do formulário: {e}")

    # 8. Teste da view
    print("\n8. Testando view de criação...")
    try:
        client = Client()

        # Criar usuário
        admin = User.objects.create_user(
            username="diag_view_admin",
            email="diagview@admin.com",
            password="test123",
            is_staff=True,
            account_type=AccountType.ADMINISTRATOR,
        )

        # Login
        client.login(username="diag_view_admin", password="test123")

        # GET request
        response = client.get(reverse("projects:produit_create"))
        print(f"   ✅ GET response status: {response.status_code}")

        # POST request
        post_data = {
            "code": "DIAG-VIEW-001",
            "name": "Produto View Test",
            "description": "Teste da view",
            "type_produit": ProductType.PAINT,
            "price_unit": "35.00",
            "unit": Unit.LITER,
            "is_active": True,
        }

        post_response = client.post(reverse("projects:produit_create"), data=post_data)
        print(f"   ✅ POST response status: {post_response.status_code}")

        # Verificar se produto foi criado
        if Product.objects.filter(code="DIAG-VIEW-001").exists():
            print("   ✅ Produto criado via view")
            Product.objects.filter(code="DIAG-VIEW-001").delete()
        else:
            print("   ❌ Produto NÃO foi criado via view")

        # Limpar
        admin.delete()

    except Exception as e:
        print(f"   ❌ Erro no teste da view: {e}")

    print("\n🏁 DIAGNÓSTICO CONCLUÍDO")
    print("=" * 60)


# Executar diagnóstico
if __name__ == "__main__":
    diagnose_product_creation()
