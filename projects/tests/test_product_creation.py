import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal
from projects.models import Product, ProductType, Unit
from projects.forms import ProduitForm
from accounts.models import AccountType

User = get_user_model()


class ProductCreationTestCase(TestCase):
    """Testes para criação de produtos"""

    def setUp(self):
        """Setup inicial para todos os testes"""
        self.client = Client()

        # Criar usuários para teste
        self.admin_user = User.objects.create_user(
            username="admin_test",
            email="admin@test.com",
            password="testpass123",
            is_staff=True,
            account_type=AccountType.ADMINISTRATOR,
        )

        self.collaborator = User.objects.create_user(
            username="collab_test",
            email="collab@test.com",
            password="testpass123",
            account_type=AccountType.COLLABORATOR,
        )

        self.client_user = User.objects.create_user(
            username="client_test",
            email="client@test.com",
            password="testpass123",
            account_type=AccountType.CLIENT,
        )

        # Dados de produto válidos
        self.valid_product_data = {
            "code": "PEIN-001",
            "name": "Peinture Acrylique Blanc",
            "description": "Peinture acrylique de qualité professionnelle",
            "type_produit": ProductType.PAINT,
            "price_unit": Decimal("25.50"),
            "unit": Unit.LITER,
            "is_active": True,
        }

    def test_product_model_creation(self):
        """Teste 1: Criação de produto via modelo"""
        print("\n🧪 TESTE 1: Criação via modelo...")

        product = Product.objects.create(**self.valid_product_data)

        # Verificações
        self.assertEqual(product.name, "Peinture Acrylique Blanc")
        self.assertEqual(product.code, "PEIN-001")
        self.assertEqual(product.type_produit, ProductType.PAINT)
        self.assertEqual(product.price_unit, Decimal("25.50"))
        self.assertEqual(product.unit, Unit.LITER)
        self.assertTrue(product.is_active)
        self.assertIsNotNone(product.id)

        print("✅ Produto criado com sucesso via modelo!")
        print(f"   ID: {product.id}")
        print(f"   Code: {product.code}")
        print(f"   Nome: {product.name}")

    def test_form_validation(self):
        """Teste 2: Validação do formulário"""
        print("\n🧪 TESTE 2: Validação do formulário...")

        # Formulário válido
        form = ProduitForm(data=self.valid_product_data)
        self.assertTrue(form.is_valid(), f"Formulário inválido: {form.errors}")

        # Formulário inválido - sem campos obrigatórios
        invalid_data = self.valid_product_data.copy()
        invalid_data["name"] = ""  # Campo obrigatório vazio

        form_invalid = ProduitForm(data=invalid_data)
        self.assertFalse(form_invalid.is_valid())

        print("✅ Validação do formulário funcionando!")

    def test_form_save(self):
        """Teste 3: Salvamento via formulário"""
        print("\n🧪 TESTE 3: Salvamento via formulário...")

        form = ProduitForm(data=self.valid_product_data)
        self.assertTrue(form.is_valid())

        product = form.save()

        # Verificar se foi salvo no banco
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(product.name, "Peinture Acrylique Blanc")

        print("✅ Formulário salvo com sucesso!")
        print(f"   Produtos no banco: {Product.objects.count()}")

    def test_admin_access_product_create_page(self):
        """Teste 4: Acesso à página de criação (Admin)"""
        print("\n🧪 TESTE 4: Acesso admin à página de criação...")

        self.client.login(username="admin_test", password="testpass123")

        response = self.client.get(reverse("projects:produit_create"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nouveau produit")

        print("✅ Admin acessa página de criação com sucesso!")

    def test_collaborator_access_product_create_page(self):
        """Teste 5: Acesso à página de criação (Colaborador)"""
        print("\n🧪 TESTE 5: Acesso colaborador à página de criação...")

        self.client.login(username="collab_test", password="testpass123")

        response = self.client.get(reverse("projects:produit_create"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nouveau produit")

        print("✅ Colaborador acessa página de criação com sucesso!")

    def test_client_denied_access(self):
        """Teste 6: Cliente não deve acessar criação de produtos"""
        print("\n🧪 TESTE 6: Cliente bloqueado...")

        self.client.login(username="client_test", password="testpass123")

        response = self.client.get(reverse("projects:produit_create"))

        # Deve redirecionar para login (bloqueado)
        self.assertEqual(response.status_code, 302)

        print("✅ Cliente corretamente bloqueado!")

    def test_product_creation_via_post(self):
        """Teste 7: Criação via POST request"""
        print("\n🧪 TESTE 7: Criação via POST...")

        self.client.login(username="admin_test", password="testpass123")

        response = self.client.post(
            reverse("projects:produit_create"), data=self.valid_product_data
        )

        # Deve redirecionar após criação bem-sucedida
        self.assertEqual(response.status_code, 302)

        # Verificar se produto foi criado
        self.assertEqual(Product.objects.count(), 1)
        product = Product.objects.first()
        self.assertEqual(product.name, "Peinture Acrylique Blanc")

        print("✅ Produto criado via POST com sucesso!")
        print(f"   Redirecionamento: {response.url}")

    def test_invalid_data_post(self):
        """Teste 8: POST com dados inválidos"""
        print("\n🧪 TESTE 8: POST com dados inválidos...")

        self.client.login(username="admin_test", password="testpass123")

        invalid_data = self.valid_product_data.copy()
        invalid_data["name"] = ""  # Campo obrigatório vazio
        invalid_data["price_unit"] = "invalid_price"  # Preço inválido

        response = self.client.post(
            reverse("projects:produit_create"), data=invalid_data
        )

        # Deve retornar à página do formulário (200) com erros
        self.assertEqual(response.status_code, 200)

        # Não deve criar produto
        self.assertEqual(Product.objects.count(), 0)

        print("✅ Dados inválidos corretamente rejeitados!")

    def test_duplicate_code_prevention(self):
        """Teste 9: Prevenção de códigos duplicados"""
        print("\n🧪 TESTE 9: Prevenção de códigos duplicados...")

        # Criar primeiro produto
        Product.objects.create(**self.valid_product_data)

        # Tentar criar segundo produto com mesmo código
        duplicate_data = self.valid_product_data.copy()
        duplicate_data["name"] = "Outro Produto"

        form = ProduitForm(data=duplicate_data)
        self.assertFalse(form.is_valid())

        print("✅ Códigos duplicados corretamente prevenidos!")

    def test_auto_code_generation(self):
        """Teste 10: Geração automática de código"""
        print("\n🧪 TESTE 10: Geração automática de código...")

        data_without_code = self.valid_product_data.copy()
        data_without_code["code"] = ""  # Sem código

        product = Product.objects.create(**data_without_code)

        # Deve ter gerado um código automaticamente
        self.assertNotEqual(product.code, "")
        self.assertTrue(len(product.code) > 0)

        print("✅ Código gerado automaticamente!")
        print(f"   Código gerado: {product.code}")


class ProductCreationIntegrationTest(TestCase):
    """Testes de integração completos"""

    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username="admin_integration",
            email="admin@integration.com",
            password="testpass123",
            is_staff=True,
            account_type=AccountType.ADMINISTRATOR,
        )

    def test_complete_workflow(self):
        """Teste de workflow completo"""
        print("\n🚀 TESTE DE INTEGRAÇÃO: Workflow completo...")

        # 1. Login
        login_success = self.client.login(
            username="admin_integration", password="testpass123"
        )
        self.assertTrue(login_success)
        print("   ✅ Login realizado")

        # 2. Acessar lista de produtos
        list_response = self.client.get(reverse("projects:produit_list"))
        self.assertEqual(list_response.status_code, 200)
        print("   ✅ Lista de produtos acessada")

        # 3. Acessar página de criação
        create_response = self.client.get(reverse("projects:produit_create"))
        self.assertEqual(create_response.status_code, 200)
        print("   ✅ Página de criação acessada")

        # 4. Criar produto
        product_data = {
            "code": "INTEG-001",
            "name": "Produto de Integração",
            "description": "Produto criado no teste de integração",
            "type_produit": ProductType.PAINT,
            "price_unit": "15.75",
            "unit": Unit.M2,
            "is_active": True,
        }

        create_post = self.client.post(
            reverse("projects:produit_create"), data=product_data
        )
        self.assertEqual(create_post.status_code, 302)  # Redirecionamento
        print("   ✅ Produto criado")

        # 5. Verificar se produto existe
        self.assertEqual(Product.objects.count(), 1)
        product = Product.objects.first()
        self.assertEqual(product.name, "Produto de Integração")
        print("   ✅ Produto verificado no banco")

        # 6. Acessar detalhes do produto
        detail_response = self.client.get(
            reverse("projects:produit_detail", kwargs={"pk": product.pk})
        )
        self.assertEqual(detail_response.status_code, 200)
        print("   ✅ Detalhes do produto acessados")

        print("\n🎉 TESTE DE INTEGRAÇÃO COMPLETO COM SUCESSO!")


class ProductDebugTest(TestCase):
    """Testes específicos para debug"""

    def test_debug_form_fields(self):
        """Debug: Verificar campos do formulário"""
        print("\n🔍 DEBUG: Campos do formulário...")

        form = ProduitForm()

        print(f"   Campos do form: {list(form.fields.keys())}")
        print(f"   Modelo do form: {form.Meta.model}")
        print(f"   Campos do modelo: {[f.name for f in form.Meta.model._meta.fields]}")

        # Verificar se todos os campos do form existem no modelo
        model_fields = [f.name for f in form.Meta.model._meta.fields]
        for field_name in form.fields.keys():
            self.assertIn(
                field_name, model_fields, f"Campo {field_name} não existe no modelo"
            )
            print(f"   ✅ Campo {field_name} existe no modelo")

    def test_debug_permissions(self):
        """Debug: Verificar permissões"""
        print("\n🔍 DEBUG: Verificar permissões...")

        # Criar usuários
        admin = User.objects.create_user(
            username="debug_admin",
            email="debug@admin.com",
            password="test123",
            is_staff=True,
            account_type=AccountType.ADMINISTRATOR,
        )

        collaborator = User.objects.create_user(
            username="debug_collab",
            email="debug@collab.com",
            password="test123",
            account_type=AccountType.COLLABORATOR,
        )

        client = User.objects.create_user(
            username="debug_client",
            email="debug@client.com",
            password="test123",
            account_type=AccountType.CLIENT,
        )

        # Importar a função de permissão
        from projects.views import can_access_products_devis

        # Testar permissões
        admin_permission = can_access_products_devis(admin)
        collab_permission = can_access_products_devis(collaborator)
        client_permission = can_access_products_devis(client)

        print(f"   Admin pode acessar: {admin_permission}")
        print(f"   Colaborador pode acessar: {collab_permission}")
        print(f"   Cliente pode acessar: {client_permission}")

        self.assertTrue(admin_permission)
        self.assertTrue(collab_permission)
        self.assertFalse(client_permission)


if __name__ == "__main__":
    # Para executar individualmente
    pytest.main([__file__, "-v"])
