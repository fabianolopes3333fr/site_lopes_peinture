"""
Teste manual das URLs do projeto.
Execute no shell: python manage.py shell
"""

from django.urls import reverse
from django.contrib.auth import get_user_model
from ..models import Project, Devis, Product
import uuid

User = get_user_model()


def test_all_urls():
    """Testa se todas as URLs estão funcionando."""

    print("🧪 TESTANDO URLs DO PROJETO")
    print("=" * 50)

    # URLs simples (sem parâmetros)
    simple_urls = [
        "projects:dashboard",
        "projects:admin_dashboard",
        "projects:list",
        "projects:create",
        "projects:devis_list",
        "projects:admin_product_list",
        "projects:admin_product_create",
    ]

    print("\n📋 URLs simples:")
    for url_name in simple_urls:
        try:
            url = reverse(url_name)
            print(f"✅ {url_name} -> {url}")
        except Exception as e:
            print(f"❌ {url_name} -> ERRO: {e}")

    # URLs com parâmetros UUID
    if Project.objects.exists():
        project = Project.objects.first()
        project_uuid = project.pk

        print(f"\n🎯 URLs com UUID do projeto: {project_uuid}")

        project_urls = [
            ("projects:detail", {"pk": project_uuid}),
            ("projects:edit", {"pk": project_uuid}),
            ("projects:delete", {"pk": project_uuid}),
            ("projects:request_quote", {"pk": project_uuid}),
            ("projects:update_status", {"pk": project_uuid}),
            ("projects:devis_create", {"project_pk": project_uuid}),
        ]

        for url_name, kwargs in project_urls:
            try:
                url = reverse(url_name, kwargs=kwargs)
                print(f"✅ {url_name} -> {url}")
            except Exception as e:
                print(f"❌ {url_name} -> ERRO: {e}")
    else:
        print("\n⚠️ Nenhum projeto encontrado para testar URLs com UUID")

    # URLs de Devis
    if Devis.objects.exists():
        devis = Devis.objects.first()
        devis_uuid = devis.pk

        print(f"\n💰 URLs de Devis com UUID: {devis_uuid}")

        devis_urls = [
            ("projects:devis_detail", {"pk": devis_uuid}),
            ("projects:devis_edit", {"pk": devis_uuid}),
            ("projects:devis_send", {"pk": devis_uuid}),
            ("projects:devis_respond", {"pk": devis_uuid}),
        ]

        for url_name, kwargs in devis_urls:
            try:
                url = reverse(url_name, kwargs=kwargs)
                print(f"✅ {url_name} -> {url}")
            except Exception as e:
                print(f"❌ {url_name} -> ERRO: {e}")
    else:
        print("\n⚠️ Nenhum devis encontrado para testar URLs com UUID")

    # URLs de Produtos
    if Product.objects.exists():
        product = Product.objects.first()
        product_uuid = product.pk

        print(f"\n🛠️ URLs de Produto com UUID: {product_uuid}")

        product_urls = [
            ("projects:admin_product_edit", {"pk": product_uuid}),
            ("projects:ajax_product_price", {"pk": product_uuid}),
        ]

        for url_name, kwargs in product_urls:
            try:
                url = reverse(url_name, kwargs=kwargs)
                print(f"✅ {url_name} -> {url}")
            except Exception as e:
                print(f"❌ {url_name} -> ERRO: {e}")
    else:
        print("\n⚠️ Nenhum produto encontrado para testar URLs com UUID")

    print(f"\n🎉 Teste de URLs concluído!")


# Para executar no shell:
# from projects.test_urls import test_all_urls
# test_all_urls()
