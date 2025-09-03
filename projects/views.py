from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import (
    ListView,
    CreateView,
    DetailView,
    UpdateView,
    DeleteView,
)
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils.translation import gettext_lazy as _
import logging

from .models import Project
from .forms import ProjectForm, ProjectStatusForm, ProjectFilterForm

logger = logging.getLogger(__name__)


class ProjectListView(LoginRequiredMixin, ListView):
    """Lista os projetos do usuário com filtros e paginação."""

    model = Project
    template_name = "projects/project_list.html"
    context_object_name = "projects"
    paginate_by = 12

    def get_queryset(self):
        """Retorna projetos do usuário com filtros aplicados."""
        queryset = Project.objects.filter(user=self.request.user)

        # Aplicar filtros
        status = self.request.GET.get("status")
        type_projet = self.request.GET.get("type_projet")
        priority = self.request.GET.get("priority")
        search = self.request.GET.get("search")

        if status:
            queryset = queryset.filter(status=status)
        if type_projet:
            queryset = queryset.filter(type_projet=type_projet)
        if priority:
            queryset = queryset.filter(priority=priority)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(description__icontains=search)
                | Q(ville__icontains=search)
            )

        return queryset.order_by("-created_at")

    def get_context_data(self, **kwargs):
        """Adiciona contexto extra para a template."""
        context = super().get_context_data(**kwargs)
        context["filter_form"] = ProjectFilterForm(self.request.GET)
        context["total_projects"] = self.get_queryset().count()

        # Estatísticas rápidas
        user_projects = Project.objects.filter(user=self.request.user)
        context["stats"] = {
            "active": user_projects.filter(
                status__in=[Project.Status.IN_PROGRESS, Project.Status.SCHEDULED]
            ).count(),
            "completed": user_projects.filter(status=Project.Status.COMPLETED).count(),
            "pending": user_projects.filter(
                status__in=[
                    Project.Status.QUOTE_REQUESTED,
                    Project.Status.QUOTE_RECEIVED,
                ]
            ).count(),
        }

        return context


class ProjectDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Exibe detalhes de um projeto específico."""

    model = Project
    template_name = "projects/project_detail.html"
    context_object_name = "project"

    def test_func(self):
        """Verifica se o usuário pode ver o projeto."""
        project = self.get_object()
        return (
            project.user == self.request.user
            or self.request.user.is_staff
            or self.request.user.has_perm("projects.view_project")
        )

    def get_context_data(self, **kwargs):
        """Adiciona contexto extra."""
        context = super().get_context_data(**kwargs)
        project = self.get_object()

        context.update(
            {
                "can_edit": (
                    project.user == self.request.user and project.can_be_edited
                )
                or self.request.user.is_staff,
                "can_delete": (
                    project.user == self.request.user or self.request.user.is_staff
                ),
                "progress_percentage": project.progress_percentage,
                "is_overdue": project.is_overdue,
            }
        )

        return context


class ProjectCreateView(LoginRequiredMixin, CreateView):
    """Cria um novo projeto."""

    model = Project
    form_class = ProjectForm
    template_name = "projects/project_form.html"

    def form_valid(self, form):
        """Associa o projeto ao usuário logado."""
        form.instance.user = self.request.user
        form.instance.status = Project.Status.DRAFT

        response = super().form_valid(form)

        messages.success(
            self.request,
            _(
                "Projet créé avec succès! Vous pouvez maintenant le modifier ou demander un devis."
            ),
        )

        logger.info(
            f"Novo projeto criado por {self.request.user.email}: {self.object.title}"
        )

        return response

    def get_success_url(self):
        return reverse_lazy("projects:detail", kwargs={"pk": self.object.pk})


class ProjectUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Edita um projeto existente."""

    model = Project
    form_class = ProjectForm
    template_name = "projects/project_form.html"

    def test_func(self):
        """Verifica se o usuário pode editar o projeto."""
        project = self.get_object()
        return (
            project.user == self.request.user and project.can_be_edited
        ) or self.request.user.is_staff

    def form_valid(self, form):
        """Processa formulário válido."""
        response = super().form_valid(form)

        messages.success(self.request, _("Projet mis à jour avec succès!"))

        logger.info(
            f"Projeto atualizado: {self.object.title} por {self.request.user.email}"
        )

        return response

    def get_success_url(self):
        return reverse_lazy("projects:detail", kwargs={"pk": self.object.pk})


class ProjectDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Exclui um projeto."""

    model = Project
    template_name = "projects/project_confirm_delete.html"
    success_url = reverse_lazy("projects:list")

    def test_func(self):
        """Verifica se o usuário pode deletar o projeto."""
        project = self.get_object()
        return project.user == self.request.user or self.request.user.is_staff

    def delete(self, request, *args, **kwargs):
        """Override para adicionar mensagem de sucesso."""
        project = self.get_object()
        project_title = project.title

        response = super().delete(request, *args, **kwargs)

        messages.success(
            request,
            _("Le projet '{title}' a été supprimé avec succès.").format(
                title=project_title
            ),
        )

        logger.info(f"Projeto deletado: {project_title} por {request.user.email}")

        return response


# Views para AJAX e funcionalidades específicas
@login_required
def project_status_update(request, pk):
    """Atualiza o status de um projeto via AJAX (para staff)."""
    if not request.user.is_staff:
        return JsonResponse({"error": "Permissão negada"}, status=403)

    project = get_object_or_404(Project, pk=pk)

    if request.method == "POST":
        form = ProjectStatusForm(request.POST, instance=project)
        if form.is_valid():
            form.save()

            return JsonResponse(
                {
                    "success": True,
                    "message": _("Statut mis à jour avec succès"),
                    "new_status": project.get_status_display(),
                    "progress": project.progress_percentage,
                }
            )
        else:
            return JsonResponse({"success": False, "errors": form.errors}, status=400)

    return JsonResponse({"error": "Méthode non autorisée"}, status=405)


@login_required
def project_dashboard(request):
    """Dashboard com visão geral dos projetos do usuário."""
    user_projects = Project.objects.filter(user=request.user)

    # Estatísticas
    stats = {
        "total": user_projects.count(),
        "active": user_projects.filter(
            status__in=[Project.Status.IN_PROGRESS, Project.Status.SCHEDULED]
        ).count(),
        "completed": user_projects.filter(status=Project.Status.COMPLETED).count(),
        "pending_quote": user_projects.filter(
            status=Project.Status.QUOTE_REQUESTED
        ).count(),
        "overdue": len([p for p in user_projects if p.is_overdue]),
    }

    # Projetos recentes
    recent_projects = user_projects.order_by("-created_at")[:5]

    # Projetos urgentes
    urgent_projects = user_projects.filter(
        priority=Project.Priority.URGENT,
        status__in=[Project.Status.IN_PROGRESS, Project.Status.SCHEDULED],
    )

    context = {
        "stats": stats,
        "recent_projects": recent_projects,
        "urgent_projects": urgent_projects,
        "page_title": _("Tableau de bord - Projets"),
    }

    return render(request, "projects/dashboard.html", context)


@login_required
def request_quote(request, pk):
    """Solicita orçamento para um projeto."""
    project = get_object_or_404(Project, pk=pk, user=request.user)

    if project.status != Project.Status.DRAFT:
        messages.warning(request, _("Un devis a déjà été demandé pour ce projet."))
        return redirect("projects:detail", pk=project.pk)

    project.status = Project.Status.QUOTE_REQUESTED
    project.save(update_fields=["status"])

    messages.success(
        request, _("Demande de devis envoyée! Nous vous contacterons bientôt.")
    )

    logger.info(
        f"Orçamento solicitado para o projeto {project.title} por {request.user.email}"
    )

    return redirect("projects:detail", pk=project.pk)
