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
    path("", views.dashboard_projects, name="dashboard"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    # ================================
    # PROJETOS - CRUD COMPLETO
    # ================================
    path("projets/", views.ProjectListView.as_view(), name="list"),
    path("projets/nouveau/", views.ProjectCreateView.as_view(), name="create"),
    path("projets/<uuid:pk>/", views.ProjectDetailView.as_view(), name="detail"),
    path("projets/<uuid:pk>/modifier/", views.ProjectUpdateView.as_view(), name="edit"),
    path(
        "projets/<uuid:pk>/supprimer/", views.ProjectDeleteView.as_view(), name="delete"
    ),
    # ================================
    # PROJETOS - AÇÕES ESPECIAIS
    # ================================
    path(
        "projets/<uuid:pk>/demander-devis/",
        views.project_request_quote,
        name="request_quote",
    ),
    path(
        "projets/<uuid:pk>/update-status/",
        views.project_update_status,
        name="update_status",
    ),
    # ================================
    # DEVIS - CRUD E GESTÃO
    # ================================
    path("devis/", views.DevisListView.as_view(), name="devis_list"),
    path("devis/<uuid:pk>/", views.DevisDetailView.as_view(), name="devis_detail"),
    path("devis/<uuid:pk>/modifier/", views.devis_edit, name="devis_edit"),
    # Criar devis para um projeto específico
    path(
        "projets/<uuid:project_pk>/creer-devis/",
        views.devis_create,
        name="devis_create",
    ),
    # ================================
    # ADMINISTRAÇÃO - PRODUTOS
    # ================================
    path("admin/produits/", views.ProductListView.as_view(), name="admin_product_list"),
    path(
        "admin/produits/nouveau/",
        views.ProductCreateView.as_view(),
        name="admin_product_create",
    ),
    path(
        "admin/produits/<uuid:pk>/modifier/",
        views.ProductUpdateView.as_view(),
        name="admin_product_edit",
    ),
    # ================================
    # AJAX E API
    # ================================
    path(
        "ajax/produit/<uuid:pk>/prix/",
        views.ajax_product_price,
        name="ajax_product_price",
    ),
    path("ajax/stats/", views.ajax_project_stats, name="ajax_project_stats"),
]

# ================================
# PADRÕES DE URL ADICIONAIS
# ================================

# URLs para filtros e buscas
search_patterns = [
    path("search/projets/", views.ProjectListView.as_view(), name="search_projects"),
    path("search/devis/", views.DevisListView.as_view(), name="search_devis"),
]

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
urlpatterns += search_patterns
# urlpatterns += report_patterns  # Descomente quando implementar
# urlpatterns += api_patterns     # Descomente quando implementar

urlpatterns += [
    # Histórico e comparação de devis
    path("devis/<uuid:pk>/history/", views.devis_history, name="devis_history"),
    path("devis/<uuid:pk>/compare/", views.devis_compare, name="devis_compare"),
    path("devis/<uuid:pk>/duplicate/", views.devis_duplicate, name="devis_duplicate"),
    # Ações de devis
    path("devis/<uuid:pk>/send/", views.devis_send, name="devis_send"),
    path("devis/<uuid:pk>/accept/", views.devis_accept, name="devis_accept"),
    path("devis/<uuid:pk>/refuse/", views.devis_refuse, name="devis_refuse"),
    path("devis/<uuid:pk>/archive/", views.devis_archive, name="devis_archive"),
    path("devis/<uuid:pk>/pdf/", views.devis_pdf, name="devis_pdf"),
    # Delete devis
    path(
        "devis/<uuid:pk>/delete/", views.DevisDeleteView.as_view(), name="devis_delete"
    ),
]
