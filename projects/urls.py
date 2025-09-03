from django.urls import path
from . import views

app_name = "projects"

urlpatterns = [
    # Dashboard
    path("dashboard/", views.project_dashboard, name="dashboard"),
    # CRUD de projetos
    path("", views.ProjectListView.as_view(), name="list"),
    path("create/", views.ProjectCreateView.as_view(), name="create"),
    path("<uuid:pk>/", views.ProjectDetailView.as_view(), name="detail"),
    path("<uuid:pk>/edit/", views.ProjectUpdateView.as_view(), name="update"),
    path("<uuid:pk>/delete/", views.ProjectDeleteView.as_view(), name="delete"),
    # Ações específicas
    path("<uuid:pk>/request-quote/", views.request_quote, name="request_quote"),
    # AJAX endpoints (para staff)
    path("<uuid:pk>/status-update/", views.project_status_update, name="status_update"),
    # URLs legacy (para compatibilidade)
    path("mes-projets/", views.ProjectListView.as_view(), name="mes_projets"),
    path("criar-projeto/", views.ProjectCreateView.as_view(), name="criar_projeto"),
    path(
        "projeto/<uuid:pk>/", views.ProjectDetailView.as_view(), name="projeto_detail"
    ),
    path(
        "projeto/<uuid:pk>/editar/",
        views.ProjectUpdateView.as_view(),
        name="editar_projeto",
    ),
    path(
        "projeto/<uuid:pk>/deletar/",
        views.ProjectDeleteView.as_view(),
        name="deletar_projeto",
    ),
]
