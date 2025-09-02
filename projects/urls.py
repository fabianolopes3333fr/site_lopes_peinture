from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name = "projects"

urlpatterns = [
    # Projetos
    path("mes-projets/", views.ProjectListView.as_view(), name="mes_projets"),
    path("criar-projeto/", views.ProjectCreateView.as_view(), name="criar_projeto"),
    path("projeto/<int:projeto_id>/", views.projeto_detail, name="projeto_detail"),
    path(
        "projeto/<int:projeto_id>/editar/", views.editar_projeto, name="editar_projeto"
    ),
    path(
        "projeto/<int:projeto_id>/deletar/",
        views.deletar_projeto,
        name="deletar_projeto",
    ),
]
