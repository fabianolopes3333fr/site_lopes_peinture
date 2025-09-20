"""
Script para testar criação de produtos manualmente
Execute: python manage.py shell < test_product_manual.py
"""

import os
import django
from decimal import Decimal

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model
from projects.models import Product, ProductType, Unit
from projects.forms import ProduitForm
from accounts.models import AccountType

User = get_user_model()


def test_product_creation():
    """Teste manual de criação de produto"""

    print("🧪 INICIANDO TESTE MANUAL DE CRIAÇÃO DE PRODUTOS")
    print("=" * 60)

    # 1. Criar usuário admin se não existir
    print("\n1. Verificando usuário admin...")
    try:
        admin_user = User.objects.get(username="admin_test_manual")
        print("   ✅ Usuário admin encontrado")
    except User.DoesNotExist:
        admin_user = User.objects.create_user(
            username="admin_test_manual",
            email="admin@test.com",
            password="test123",
            is_staff=True,
            account_type=AccountType.ADMINISTRATOR,
        )
        print("   ✅ Usuário admin criado")

    # 2. Testar modelo Product
    print("\n2. Testando modelo Product...")

    product_data = {
        "code": "TEST-MANUAL-001",
        "name": "Produto Teste Manual",
        "description": "Produto criado no teste manual",
        "type_produit": ProductType.PAINT,
        "price_unit": Decimal("29.99"),
        "unit": Unit.LITER,
        "is_active": True,
    }

    try:
        product = Product.objects.create(**product_data)
        print(f"   ✅ Produto criado: {product}")
        print(f"   ✅ ID: {product.id}")
        print(f"   ✅ Code: {product.code}")
        print(f"   ✅ Nome: {product.name}")
        print(f"   ✅ Preço: {product.price_unit}")
    except Exception as e:
        print(f"   ❌ Erro ao criar produto: {e}")
        return False

    # 3. Testar formulário
    print("\n3. Testando formulário...")

    form_data = {
        "code": "TEST-FORM-001",
        "name": "Produto Formulário",
        "description": "Produto criado via formulário",
        "type_produit": ProductType.MATERIAL,
        "price_unit": "19.50",
        "unit": Unit.UNIT,
        "is_active": True,
    }

    try:
        form = ProduitForm(data=form_data)
        if form.is_valid():
            form_product = form.save()
            print(f"   ✅ Produto via formulário: {form_product}")
        else:
            print(f"   ❌ Formulário inválido: {form.errors}")
            return False
    except Exception as e:
        print(f"   ❌ Erro no formulário: {e}")
        return False

    # 4. Verificar produtos criados
    print("\n4. Verificando produtos no banco...")

    total_products = Product.objects.count()
    test_products = Product.objects.filter(code__startswith="TEST-")

    print(f"   ✅ Total de produtos: {total_products}")
    print(f"   ✅ Produtos de teste: {test_products.count()}")

    for p in test_products:
        print(f"      - {p.code}: {p.name} (€{p.price_unit})")

    # 5. Testar choices
    print("\n5. Verificando choices...")

    print("   ProductType choices:")
    for value, label in ProductType.choices:
        print(f"      {value}: {label}")

    print("   Unit choices:")
    for value, label in Unit.choices:
        print(f"      {value}: {label}")

    # 6. Testar validações
    print("\n6. Testando validações...")

    # Código duplicado
    duplicate_form = ProduitForm(
        data={
            "code": "TEST-MANUAL-001",  # Código já existe
            "name": "Produto Duplicado",
            "type_produit": ProductType.PAINT,
            "price_unit": "10.00",
            "unit": Unit.M2,
            "is_active": True,
        }
    )

    if not duplicate_form.is_valid():
        print("   ✅ Código duplicado corretamente rejeitado")
    else:
        print("   ⚠️  Código duplicado aceito (problema!)")

    print("\n🎉 TESTE MANUAL CONCLUÍDO COM SUCESSO!")
    print("=" * 60)

    return True


# Executar teste
if __name__ == "__main__":
    test_product_creation()
