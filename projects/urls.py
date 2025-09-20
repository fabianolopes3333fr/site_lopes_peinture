from django.urls import path, include
from . import views

app_name = "projects"

# ================================
# URLS PRINCIPAIS
# ================================

urlpatterns = [
    # ================================
    # DASHBOARDS
    # ================================
    path("admin/", views.dashboard_projects, name="admin_dashboard"),
    # ================================
    # PROJETOS - CRUD COMPLETO
    # ================================
    path("projets/", views.projet_list, name="projet_list"),
    path("projets/nouveau/", views.projet_create_step1, name="projet_create_step1"),
    path(
        "projets/nouveau/step2/", views.projet_create_step2, name="projet_create_step2"
    ),
    path(
        "projets/nouveau/step3/", views.projet_create_step3, name="projet_create_step3"
    ),
    path("projets/<uuid:pk>/", views.projet_detail, name="projet_detail"),
    path("projets/<uuid:pk>/modifier/", views.projet_update, name="projet_update"),
    path("projets/<uuid:pk>/supprimer/", views.projet_delete, name="projet_delete"),
    path(
        "projets/<uuid:pk>/devis/nouveau/",
        views.projet_create_devis,
        name="projet_create_devis",
    ),
    # ================================
    # DEVIS - CRUD E GESTÃO
    # ================================
    path("devis/", views.devis_list, name="devis_list"),
    path("devis/<uuid:pk>/", views.devis_detail, name="devis_detail"),
    path("devis/<uuid:pk>/supprimer/", views.devis_delete, name="devis_delete"),
    path("devis/<uuid:pk>/pdf/", views.devis_pdf, name="devis_pdf"),
    # ================================
    # PROJETOS - AÇÕES ESPECIAIS
    # ================================
    path("produits/", views.produit_list, name="produit_list"),
    path("produits/nouveau/", views.produit_create, name="produit_create"),
    path("produits/<uuid:pk>/", views.produit_detail, name="produit_detail"),
    path("produits/<uuid:pk>/modifier/", views.produit_update, name="produit_update"),
    path("produits/<uuid:pk>/supprimer/", views.produit_delete, name="produit_delete"),
    # ================================
    # AJAX E API
    # ================================
]

# ================================
# PADRÕES DE URL ADICIONAIS
# ================================

# URLs para filtros e buscas


# URLs para relatórios (futuro)
report_patterns = [
    # path('rapports/projets/', views.ProjectReportView.as_view(), name='project_reports'),
    # path('rapports/devis/', views.DevisReportView.as_view(), name='devis_reports'),
]

# URLs para API (futuro)
api_patterns = [
    # path('api/projets/', views.ProjectApiView.as_view(), name='api_projects'),
    # path('api/devis/', views.DevisApiView.as_view(), name='api_devis'),
]

# Adicionar padrões extras
# urlpatterns += search_patterns
# urlpatterns += report_patterns  # Descomente quando implementar
# urlpatterns += api_patterns     # Descomente quando implementar

urlpatterns += [
    # Histórico e comparação de devis
    # path("devis/<uuid:pk>/history/", views.devis_history, name="devis_history"),
    # path("devis/<uuid:pk>/compare/", views.devis_compare, name="devis_compare"),
    # path("devis/<uuid:pk>/duplicate/", views.devis_duplicate, name="devis_duplicate"),
    # Ações de devis
    path("devis/<uuid:pk>/send/", views.devis_send, name="devis_send"),
    # path("devis/<uuid:pk>/refuse/", views.devis_refuse, name="devis_refuse"),
    # path("devis/<uuid:pk>/archive/", views.devis_archive, name="devis_archive"),
    # path("devis/<uuid:pk>/pdf/", views.devis_pdf, name="devis_pdf"),
    # Delete devis
]
