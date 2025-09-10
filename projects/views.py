from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum, Avg
from django.http import JsonResponse, HttpResponse, Http404
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView,
)
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.conf import settings
import logging
from decimal import Decimal
import json

from .models import Project, Devis, DevisLine, Product, DevisHistory
from .forms import (
    ProjectForm,
    ProjectStatusForm,
    DevisForm,
    DevisLineForm,
    ProductForm,
    DevisStatusForm,
    DevisLineFormSet,
    ProjectFilterForm,
    DevisFilterForm,
)

logger = logging.getLogger(__name__)
User = get_user_model()


def is_staff(user):
    """Verifica se o usuário é staff."""
    return user.is_authenticated and user.is_staff


def can_edit_project(user, project):
    """Verifica se o usuário pode editar o projeto."""
    return user == project.user or user.is_staff


# ================================
# VIEWS DE DASHBOARD
# ================================


@login_required
def dashboard_projects(request):
    """
    Dashboard principal de projetos para o usuário.
    """
    user = request.user

    # Estatísticas básicas
    projects = Project.objects.filter(user=user)
    total_projects = projects.count()
    active_projects = projects.exclude(
        status__in=[Project.Status.COMPLETED, Project.Status.CANCELLED]
    ).count()
    completed_projects = projects.filter(status=Project.Status.COMPLETED).count()

    # Projetos recentes
    recent_projects = projects.order_by("-created_at")[:5]

    # Devis pendentes
    pending_devis = Devis.objects.filter(
        project__user=user, status__in=[Devis.Status.SENT, Devis.Status.VIEWED]
    ).order_by("-date_created")[:5]

    # Estatísticas por status
    status_stats = {}
    for status, label in Project.Status.choices:
        count = projects.filter(status=status).count()
        if count > 0:
            status_stats[label] = count

    context = {
        "total_projects": total_projects,
        "active_projects": active_projects,
        "completed_projects": completed_projects,
        "recent_projects": recent_projects,
        "pending_devis": pending_devis,
        "status_stats": status_stats,
    }

    return render(request, "projects/dashboard.html", context)


@user_passes_test(is_staff)
def admin_dashboard(request):
    """
    Dashboard administrativo.
    """
    # Estatísticas gerais
    total_projects = Project.objects.count()
    total_users = User.objects.filter(is_staff=False).count()
    total_devis = Devis.objects.count()
    total_products = Product.objects.filter(is_active=True).count()

    # Projetos por status
    projects_by_status = {}
    for status, label in Project.Status.choices:
        count = Project.objects.filter(status=status).count()
        if count > 0:
            projects_by_status[label] = count

    # Devis por status
    devis_by_status = {}
    for status, label in Devis.Status.choices:
        count = Devis.objects.filter(status=status).count()
        if count > 0:
            devis_by_status[label] = count

    # Projetos recentes
    recent_projects = Project.objects.select_related("user").order_by("-created_at")[
        :10
    ]

    # Devis pendentes de resposta
    pending_devis = (
        Devis.objects.select_related("project", "project__user")
        .filter(status__in=[Devis.Status.SENT, Devis.Status.VIEWED])
        .order_by("-date_created")[:10]
    )

    context = {
        "total_projects": total_projects,
        "total_users": total_users,
        "total_devis": total_devis,
        "total_products": total_products,
        "projects_by_status": projects_by_status,
        "devis_by_status": devis_by_status,
        "recent_projects": recent_projects,
        "pending_devis": pending_devis,
    }

    return render(request, "projects/admin_dashboard.html", context)


# ================================
# VIEWS DE PROJETOS
# ================================


class ProjectListView(LoginRequiredMixin, ListView):
    """
    Listagem de projetos do usuário com filtros.
    """

    model = Project
    template_name = "projects/project_list.html"
    context_object_name = "projects"
    paginate_by = 12

    def get_queryset(self):
        """Filtrar projetos do usuário com filtros aplicados."""
        queryset = Project.objects.filter(user=self.request.user)

        # Aplicar filtros
        form = ProjectFilterForm(self.request.GET)
        if form.is_valid():
            search = form.cleaned_data.get("search")
            status = form.cleaned_data.get("status")
            type_projet = form.cleaned_data.get("type_projet")
            priority = form.cleaned_data.get("priority")
            date_from = form.cleaned_data.get("date_from")
            date_to = form.cleaned_data.get("date_to")

            if search:
                queryset = queryset.filter(
                    Q(title__icontains=search)
                    | Q(description__icontains=search)
                    | Q(reference__icontains=search)
                    | Q(ville__icontains=search)
                )

            if status:
                queryset = queryset.filter(status=status)

            if type_projet:
                queryset = queryset.filter(type_projet=type_projet)

            if priority:
                queryset = queryset.filter(priority=priority)

            if date_from:
                queryset = queryset.filter(created_at__date__gte=date_from)

            if date_to:
                queryset = queryset.filter(created_at__date__lte=date_to)

        return queryset.order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter_form"] = ProjectFilterForm(self.request.GET)

        # Estatísticas para o sidebar
        user_projects = Project.objects.filter(user=self.request.user)
        context["total_projects"] = user_projects.count()
        context["active_projects"] = user_projects.exclude(
            status__in=[Project.Status.COMPLETED, Project.Status.CANCELLED]
        ).count()

        return context


class ProjectDetailView(LoginRequiredMixin, DetailView):
    """
    Visualização detalhada do projeto.
    """

    model = Project
    template_name = "projects/project_detail.html"
    context_object_name = "project"

    def get_queryset(self):
        """Usuário só pode ver seus próprios projetos ou staff vê todos."""
        if self.request.user.is_staff:
            return Project.objects.all()
        return Project.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.object

        # Devis relacionados
        context["devis_list"] = project.devis.all().order_by("-date_created")

        # Permissões
        context["can_edit"] = can_edit_project(self.request.user, project)
        context["can_request_quote"] = project.can_request_quote
        context["is_staff"] = self.request.user.is_staff

        # Status form para admin
        if self.request.user.is_staff:
            context["status_form"] = ProjectStatusForm(instance=project)

        return context


class ProjectCreateView(LoginRequiredMixin, CreateView):
    """
    Criação de novo projeto.
    """

    model = Project
    form_class = ProjectForm
    template_name = "projects/project_create.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        logger.info(f"Criando novo projeto para {self.request.user.email}")

        form.instance.user = self.request.user
        response = super().form_valid(form)

        messages.success(
            self.request,
            f"✅ Projet '{self.object.title}' créé avec succès! Référence: {self.object.reference}",
        )

        logger.info(f"Projeto criado: {self.object.reference}")
        return response

    def get_success_url(self):
        return reverse("projects:detail", kwargs={"pk": self.object.pk})


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    """
    Edição de projeto.
    """

    model = Project
    form_class = ProjectForm
    template_name = "projects/project_edit.html"

    def get_queryset(self):
        """Usuário só pode editar seus próprios projetos."""
        if self.request.user.is_staff:
            return Project.objects.all()
        return Project.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        """Verificar se o projeto pode ser editado."""
        project = self.get_object()
        if not project.can_be_edited and not request.user.is_staff:
            messages.error(request, "Ce projet ne peut plus être modifié.")
            return redirect("projects:detail", pk=project.pk)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, "✅ Projet mis à jour avec succès!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("projects:detail", kwargs={"pk": self.object.pk})


# ================================
# DELETE VIEWS - PROJETOS E DEVIS
# ================================


class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    """
    View para deletar projetos com confirmação de segurança
    """

    model = Project
    template_name = "projects/project_delete.html"
    context_object_name = "project"

    def get_queryset(self):
        """Filtrar projetos baseado nas permissões do usuário"""
        if self.request.user.is_staff:
            return Project.objects.all()
        return Project.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_object()

        # Verificar se pode ser deletado
        context["can_be_deleted"] = project.can_be_deleted()

        # Adicionar informações de dependências
        context["dependencies"] = {
            "photos_count": project.photos.count() if hasattr(project, "photos") else 0,
            "comments_count": (
                project.comments.count() if hasattr(project, "comments") else 0
            ),
            "devis_count": project.devis.count(),
            "devis_sent_count": project.devis.exclude(status="brouillon").count(),
        }

        return context

    def delete(self, request, *args, **kwargs):
        """Override delete para adicionar validações e logging"""
        project = self.get_object()

        # Verificar se pode ser deletado
        if not project.can_be_deleted():
            messages.error(
                request,
                "Ce projet ne peut pas être supprimé en raison de son statut ou des éléments associés.",
            )
            return redirect("projects:detail", pk=project.pk)

        # Verificar se usuário tem permissão
        if not request.user.is_staff and project.user != request.user:
            messages.error(
                request, "Vous n'avez pas l'autorisation de supprimer ce projet."
            )
            return redirect("projects:detail", pk=project.pk)

        # Log da ação
        project_title = project.title
        project_reference = project.reference

        try:
            # Deletar projeto
            response = super().delete(request, *args, **kwargs)

            # Notificar equipe se não for staff
            if not request.user.is_staff:
                # send_project_deletion_notification(project_reference, request.user)
                pass

            messages.success(
                request,
                f"Projet '{project_title}' ({project_reference}) supprimé avec succès.",
            )

            return response

        except Exception as e:
            messages.error(request, f"Erreur lors de la suppression: {str(e)}")
            return redirect("projects:detail", pk=project.pk)

    def get_success_url(self):
        """Rediriger vers dashboard après suppression"""
        return reverse_lazy("projects:dashboard")


@login_required
@require_POST
@csrf_protect
def project_request_quote(request, pk):
    """
    Solicitar orçamento para um projeto.
    """
    project = get_object_or_404(Project, pk=pk, user=request.user)

    if not project.can_request_quote:
        messages.error(request, "Impossible de demander un devis pour ce projet.")
        return redirect("projects:detail", pk=pk)

    # Atualizar status
    project.status = Project.Status.QUOTE_REQUESTED
    project.save(update_fields=["status"])

    messages.success(
        request,
        "✅ Demande de devis envoyée! Nous vous contacterons dans les plus brefs délais.",
    )

    logger.info(
        f"Devis solicitado para projeto {project.reference} por {request.user.email}"
    )

    return redirect("projects:detail", pk=pk)


@user_passes_test(is_staff)
@require_POST
@csrf_protect
def project_update_status(request, pk):
    """
    Atualizar status do projeto (apenas admin).
    """
    project = get_object_or_404(Project, pk=pk)
    form = ProjectStatusForm(request.POST, instance=project)

    if form.is_valid():
        form.save()
        messages.success(request, "✅ Statut du projet mis à jour!")
        logger.info(
            f"Status do projeto {project.reference} atualizado para {project.status}"
        )
    else:
        for error in form.errors.values():
            messages.error(request, f"❌ {error}")

    return redirect("projects:detail", pk=pk)


# ================================
# VIEWS DE DEVIS
# ================================


class DevisListView(LoginRequiredMixin, ListView):
    """
    Listagem de devis do usuário.
    """

    model = Devis
    template_name = "projects/devis_list.html"
    context_object_name = "devis_list"
    paginate_by = 12

    def get_queryset(self):
        """Filtrar devis do usuário."""
        queryset = Devis.objects.filter(project__user=self.request.user)

        # Aplicar filtros
        form = DevisFilterForm(self.request.GET, user=self.request.user)
        if form.is_valid():
            search = form.cleaned_data.get("search")
            status = form.cleaned_data.get("status")
            project = form.cleaned_data.get("project")

            if search:
                queryset = queryset.filter(
                    Q(title__icontains=search)
                    | Q(reference__icontains=search)
                    | Q(project__title__icontains=search)
                )

            if status:
                queryset = queryset.filter(status=status)

            if project:
                queryset = queryset.filter(project=project)

        return queryset.select_related("project").order_by("-date_created")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter_form"] = DevisFilterForm(
            self.request.GET, user=self.request.user
        )

        # Estatísticas
        user_devis = Devis.objects.filter(project__user=self.request.user)
        context["total_devis"] = user_devis.count()
        context["pending_devis"] = user_devis.filter(
            status__in=[Devis.Status.SENT, Devis.Status.VIEWED]
        ).count()

        return context


class DevisDetailView(LoginRequiredMixin, DetailView):
    """
    Visualização detalhada do devis.
    """

    model = Devis
    template_name = "projects/devis_detail.html"
    context_object_name = "devis"

    def get_queryset(self):
        """Usuário só pode ver devis de seus projetos."""
        if self.request.user.is_staff:
            return Devis.objects.all()
        return Devis.objects.filter(project__user=self.request.user)

    def get_object(self, queryset=None):
        """Marcar como visualizado quando cliente acessa."""
        devis = super().get_object(queryset)

        # Se não é staff e devis foi enviado, marcar como visualizado
        if (
            not self.request.user.is_staff
            and devis.status == Devis.Status.SENT
            and devis.project.user == self.request.user
        ):

            devis.status = Devis.Status.VIEWED
            devis.date_viewed = timezone.now()
            devis.save(update_fields=["status", "date_viewed"])

            # Adicionar ao histórico
            DevisHistory.objects.create(
                devis=devis,
                action=DevisHistory.ActionType.VIEWED,
                user=self.request.user,
                notes="Devis consulté par le client",
            )

        return devis

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        devis = self.object

        # Linhas do devis
        context["devis_lines"] = devis.lines.select_related("product").order_by(
            "order", "id"
        )

        # Histórico (apenas para staff)
        if self.request.user.is_staff:
            context["history"] = devis.history.select_related("user").order_by(
                "-timestamp"
            )

        # Permissões
        context["can_accept"] = (
            devis.can_be_accepted and devis.project.user == self.request.user
        )
        context["can_edit"] = (
            self.request.user.is_staff and devis.status == Devis.Status.DRAFT
        )
        context["is_staff"] = self.request.user.is_staff

        return context


@user_passes_test(is_staff)
def devis_create(request, project_pk):
    """
    Criar novo devis para um projeto (apenas admin).
    """
    project = get_object_or_404(Project, pk=project_pk)

    if request.method == "POST":
        form = DevisForm(request.POST, project=project, user=request.user)
        formset = DevisLineFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            devis = form.save()

            # Salvar linhas
            formset.instance = devis
            formset.save()

            # Recalcular totais
            devis.calculate_totals()

            # Atualizar status do projeto
            project.status = Project.Status.QUOTE_SENT
            project.save(update_fields=["status"])

            # Adicionar ao histórico
            DevisHistory.objects.create(
                devis=devis,
                action=DevisHistory.ActionType.CREATED,
                user=request.user,
                notes=f"Devis créé par {request.user.get_full_name()}",
            )

            messages.success(request, f"✅ Devis '{devis.reference}' créé avec succès!")
            logger.info(
                f"Devis criado: {devis.reference} para projeto {project.reference}"
            )

            return redirect("projects:devis_detail", pk=devis.pk)
    else:
        form = DevisForm(project=project, user=request.user)
        formset = DevisLineFormSet()

    context = {
        "form": form,
        "formset": formset,
        "project": project,
    }

    return render(request, "projects/devis_create.html", context)


@user_passes_test(is_staff)
def devis_edit(request, pk):
    """
    Editar devis (apenas admin).
    """
    devis = get_object_or_404(Devis, pk=pk)

    if devis.status != Devis.Status.DRAFT:
        messages.error(request, "Ce devis ne peut plus être modifié.")
        return redirect("projects:devis_detail", pk=pk)

    if request.method == "POST":
        form = DevisForm(request.POST, instance=devis)
        formset = DevisLineFormSet(request.POST, instance=devis)

        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()

            # Recalcular totais
            devis.calculate_totals()

            messages.success(request, "✅ Devis mis à jour avec succès!")
            return redirect("projects:devis_detail", pk=pk)
    else:
        form = DevisForm(instance=devis)
        formset = DevisLineFormSet(instance=devis)

    context = {
        "form": form,
        "formset": formset,
        "devis": devis,
    }

    return render(request, "projects/devis_edit.html", context)


@user_passes_test(is_staff)
@login_required
@require_http_methods(["POST"])
def devis_send(request, pk):
    """
    View para enviar um devis ao cliente
    """
    try:
        if not request.user.is_staff:
            messages.error(
                request, "Vous n'avez pas l'autorisation d'envoyer des devis."
            )
            return redirect("projects:devis_detail", pk=pk)

        devis = get_object_or_404(Devis, pk=pk)

        if devis.status != "brouillon":
            messages.error(
                request, "Seuls les devis en brouillon peuvent être envoyés."
            )
            return redirect("projects:devis_detail", pk=pk)

        # Valider que le devis est complet
        if not devis.items.exists():
            messages.error(
                request, "Le devis doit contenir au moins un item avant d'être envoyé."
            )
            return redirect("projects:devis_edit", pk=pk)

        # Mettre à jour le status et la date d'envoi
        devis.status = "envoye"
        devis.sent_at = timezone.now()
        devis.save()

        # Envoyer email au client (à implémenter)
        try:
            # send_devis_email(devis)
            pass
        except Exception as email_error:
            messages.warning(
                request, f"Devis envoyé mais erreur email: {str(email_error)}"
            )

        # Mettre à jour le status du projet
        project = devis.project
        if project.status in ["nouveau", "en_examen"]:
            project.status = "devis_envoye"
            project.save()

        messages.success(
            request, f"Devis {devis.reference} envoyé avec succès au client."
        )

        return redirect("projects:devis_detail", pk=pk)

    except Exception as e:
        messages.error(request, f"Erreur lors de l'envoi: {str(e)}")
        return redirect("projects:devis_detail", pk=pk)


# ================================
# VIEWS DE PRODUTOS (ADMIN)
# ================================


@method_decorator(user_passes_test(is_staff), name="dispatch")
class ProductListView(ListView):
    """
    Listagem de produtos (apenas admin).
    """

    model = Product
    template_name = "projects/admin/product_list.html"
    context_object_name = "products"
    paginate_by = 20

    def get_queryset(self):
        queryset = Product.objects.all()

        search = self.request.GET.get("search")
        type_filter = self.request.GET.get("type")
        active_filter = self.request.GET.get("active")

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(code__icontains=search)
                | Q(description__icontains=search)
            )

        if type_filter:
            queryset = queryset.filter(type_product=type_filter)

        if active_filter == "true":
            queryset = queryset.filter(is_active=True)
        elif active_filter == "false":
            queryset = queryset.filter(is_active=False)

        return queryset.order_by("type_product", "name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = self.request.GET.get("search", "")
        context["type_filter"] = self.request.GET.get("type", "")
        context["active_filter"] = self.request.GET.get("active", "")
        context["product_types"] = Product.ProductType.choices
        return context


@method_decorator(user_passes_test(is_staff), name="dispatch")
class ProductCreateView(CreateView):
    """
    Criar produto (apenas admin).
    """

    model = Product
    form_class = ProductForm
    template_name = "projects/admin/product_create.html"
    success_url = reverse_lazy("projects:admin_product_list")

    def form_valid(self, form):
        messages.success(
            self.request, f"✅ Produit '{form.instance.name}' créé avec succès!"
        )
        return super().form_valid(form)


@method_decorator(user_passes_test(is_staff), name="dispatch")
class ProductUpdateView(UpdateView):
    """
    Editar produto (apenas admin).
    """

    model = Product
    form_class = ProductForm
    template_name = "projects/admin/product_edit.html"
    success_url = reverse_lazy("projects:admin_product_list")

    def form_valid(self, form):
        messages.success(self.request, f"✅ Produit '{form.instance.name}' mis à jour!")
        return super().form_valid(form)


# ================================
# AJAX VIEWS
# ================================


@login_required
def ajax_product_price(request, pk):
    """
    Retornar preço do produto via AJAX.
    """
    try:
        product = Product.objects.get(pk=pk, is_active=True)
        return JsonResponse(
            {
                "success": True,
                "price": float(product.price_unit),
                "unit": product.get_unit_display(),
            }
        )
    except Product.DoesNotExist:
        return JsonResponse({"success": False, "error": "Produto não encontrado"})


@user_passes_test(is_staff)
def ajax_project_stats(request):
    """
    Estatísticas dos projetos via AJAX (admin).
    """
    stats = {}

    for status, label in Project.Status.choices:
        count = Project.objects.filter(status=status).count()
        stats[status] = {"label": label, "count": count}

    return JsonResponse({"success": True, "stats": stats})


# ================================
# VIEWS PARA DEVIS - FUNCIONALIDADES AVANÇADAS
# ================================


@login_required
def devis_history(request, pk):
    """
    View para exibir o histórico completo de um devis
    """
    try:
        if request.user.is_staff:
            devis = get_object_or_404(Devis, pk=pk)
        else:
            devis = get_object_or_404(Devis, pk=pk, project__user=request.user)

        # Buscar histórico do devis (assumindo que você tem um modelo de histórico)
        # Se não tiver, pode usar django-simple-history ou criar um sistema próprio
        history_items = []

        # Histórico básico baseado em campos do modelo
        history_data = [
            {
                "action": "Création",
                "date": devis.created_at,
                "user": "Système",
                "details": f"Devis créé pour le projet {devis.project.title}",
                "icon": "fas fa-plus",
                "color": "blue",
            }
        ]

        if devis.sent_at:
            history_data.append(
                {
                    "action": "Envoi au client",
                    "date": devis.sent_at,
                    "user": "Équipe LOPES PEINTURE",
                    "details": f"Devis envoyé au client ({devis.project.user.email})",
                    "icon": "fas fa-paper-plane",
                    "color": "green",
                }
            )

        if devis.status == "accepte":
            history_data.append(
                {
                    "action": "Acceptation",
                    "date": devis.updated_at,
                    "user": devis.project.user.get_full_name()
                    or devis.project.user.username,
                    "details": f"Devis accepté par le client",
                    "icon": "fas fa-check-circle",
                    "color": "green",
                }
            )
        elif devis.status == "refuse":
            history_data.append(
                {
                    "action": "Refus",
                    "date": devis.updated_at,
                    "user": devis.project.user.get_full_name()
                    or devis.project.user.username,
                    "details": f"Devis refusé par le client",
                    "icon": "fas fa-times-circle",
                    "color": "red",
                }
            )

        # Ajouter modifications (versions)
        if devis.version > 1:
            history_data.append(
                {
                    "action": f"Version {devis.version}",
                    "date": devis.updated_at,
                    "user": "Équipe LOPES PEINTURE",
                    "details": f"Nouvelle version du devis créée",
                    "icon": "fas fa-code-branch",
                    "color": "purple",
                }
            )

        # Trier par date
        history_data.sort(key=lambda x: x["date"], reverse=True)

        context = {
            "devis": devis,
            "history_items": history_data,
        }

        return render(request, "projects/devis_history.html", context)

    except Exception as e:
        messages.error(request, f"Erreur lors du chargement de l'historique: {str(e)}")
        return redirect("projects:devis_detail", pk=pk)


@login_required
def devis_compare(request, pk):
    """
    View para comparar versões de um devis
    """
    try:
        if request.user.is_staff:
            devis = get_object_or_404(Devis, pk=pk)
        else:
            devis = get_object_or_404(Devis, pk=pk, project__user=request.user)

        # Buscar versões anteriores do mesmo projeto
        # Assumindo que você tem um campo 'original_devis' ou similar para rastrear versões
        all_versions = Devis.objects.filter(project=devis.project).order_by("version")

        # Se não houver sistema de versioning, criar dados de comparação básicos
        comparison_data = {
            "current": {
                "version": devis.version,
                "title": devis.title,
                "total": devis.total,
                "items_count": devis.items.count() if hasattr(devis, "items") else 0,
                "status": devis.get_status_display(),
                "created": devis.created_at,
                "description": devis.description,
            }
        }

        previous_version = None
        if all_versions.count() > 1:
            # Pegar a versão anterior
            previous_versions = all_versions.exclude(pk=devis.pk)
            if previous_versions.exists():
                previous_version = previous_versions.last()
                comparison_data["previous"] = {
                    "version": previous_version.version,
                    "title": previous_version.title,
                    "total": previous_version.total,
                    "items_count": (
                        previous_version.items.count()
                        if hasattr(previous_version, "items")
                        else 0
                    ),
                    "status": previous_version.get_status_display(),
                    "created": previous_version.created_at,
                    "description": previous_version.description,
                }

        # Calcular diferenças
        differences = []
        if previous_version:
            if devis.title != previous_version.title:
                differences.append(
                    {
                        "field": "Titre",
                        "old_value": previous_version.title,
                        "new_value": devis.title,
                        "type": "modified",
                    }
                )

            if devis.total != previous_version.total:
                differences.append(
                    {
                        "field": "Montant total",
                        "old_value": f"{previous_version.total}€",
                        "new_value": f"{devis.total}€",
                        "type": "modified",
                    }
                )

            if devis.description != previous_version.description:
                differences.append(
                    {
                        "field": "Description",
                        "old_value": previous_version.description,
                        "new_value": devis.description,
                        "type": "modified",
                    }
                )

        context = {
            "devis": devis,
            "previous_version": previous_version,
            "all_versions": all_versions,
            "comparison_data": comparison_data,
            "differences": differences,
        }

        return render(request, "projects/devis_compare.html", context)

    except Exception as e:
        messages.error(request, f"Erreur lors de la comparaison: {str(e)}")
        return redirect("projects:devis_detail", pk=pk)


@login_required
def devis_duplicate(request, pk):
    """
    View para duplicar um devis
    """
    try:
        if request.user.is_staff:
            original_devis = get_object_or_404(Devis, pk=pk)
        else:
            original_devis = get_object_or_404(Devis, pk=pk, project__user=request.user)

        # Criar uma cópia do devis
        new_devis = Devis.objects.create(
            project=original_devis.project,
            title=f"Copie de {original_devis.title}",
            description=original_devis.description,
            # Não copiar: reference (será gerada automaticamente), status (será brouillon)
            tax_rate=original_devis.tax_rate,
            discount_percentage=original_devis.discount_percentage,
            terms_conditions=original_devis.terms_conditions,
            notes=original_devis.notes,
            date_expiry=None,  # Resetar data de expiração
            version=1,  # Nova versão
            status="brouillon",  # Sempre começar como brouillon
        )

        # Copiar items se existirem
        if hasattr(original_devis, "items"):
            for item in original_devis.items.all():
                # Assumindo que você tem um modelo DevisItem
                item.pk = None  # Remove o ID para criar novo
                item.devis = new_devis
                item.save()

        messages.success(
            request,
            f"Devis dupliqué avec succès. Nouvelle référence: {new_devis.reference}",
        )

        return redirect("projects:devis_edit", pk=new_devis.pk)

    except Exception as e:
        messages.error(request, f"Erreur lors de la duplication: {str(e)}")
        return redirect("projects:devis_detail", pk=pk)


@login_required
@require_http_methods(["POST"])
def devis_accept(request, pk):
    """
    View para cliente aceitar um devis
    """
    try:
        devis = get_object_or_404(Devis, pk=pk, project__user=request.user)

        if devis.status != "envoye":
            messages.error(
                request, "Ce devis ne peut pas être accepté dans son état actuel."
            )
            return redirect("projects:devis_detail", pk=pk)

        if devis.is_expired:
            messages.error(request, "Ce devis a expiré et ne peut plus être accepté.")
            return redirect("projects:devis_detail", pk=pk)

        # Accepter le devis
        devis.status = "accepte"
        devis.accepted_at = timezone.now()
        devis.save()

        # Mettre à jour le projet
        project = devis.project
        project.status = "accepte"
        project.save()

        # Envoyer notification à l'équipe (à implémenter)
        # send_devis_accepted_notification(devis)

        messages.success(request, f"Devis {devis.reference} accepté avec succès!")

        return redirect("projects:devis_detail", pk=pk)

    except Exception as e:
        messages.error(request, f"Erreur lors de l'acceptation: {str(e)}")
        return redirect("projects:devis_detail", pk=pk)


@login_required
@require_http_methods(["POST"])
def devis_refuse(request, pk):
    """
    View para cliente recusar um devis
    """
    try:
        devis = get_object_or_404(Devis, pk=pk, project__user=request.user)

        if devis.status != "envoye":
            messages.error(
                request, "Ce devis ne peut pas être refusé dans son état actuel."
            )
            return redirect("projects:devis_detail", pk=pk)

        # Recusar o devis
        devis.status = "refuse"
        devis.refused_at = timezone.now()
        devis.save()

        # Mettre à jour le projet (opcional - pode querer manter como devis_envoye)
        project = devis.project
        project.status = "refuse"
        project.save()

        # Envoyer notification à l'équipe (à implémenter)
        # send_devis_refused_notification(devis)

        messages.info(request, f"Devis {devis.reference} refusé.")

        return redirect("projects:devis_detail", pk=pk)

    except Exception as e:
        messages.error(request, f"Erreur lors du refus: {str(e)}")
        return redirect("projects:devis_detail", pk=pk)


@login_required
@require_http_methods(["POST"])
def devis_archive(request, pk):
    """
    View para arquivar um devis (alternativa à suppression)
    """
    try:
        if not request.user.is_staff:
            messages.error(
                request, "Vous n'avez pas l'autorisation d'archiver des devis."
            )
            return redirect("projects:devis_detail", pk=pk)

        devis = get_object_or_404(Devis, pk=pk)

        # Adicionar campo 'archived' ao modelo ou usar soft delete
        # devis.archived = True
        # devis.archived_at = timezone.now()
        # devis.archived_by = request.user
        # devis.save()

        # Se não tiver campo archived, pode usar status
        devis.status = "archive"
        devis.save()

        messages.success(request, f"Devis {devis.reference} archivé avec succès.")

        return redirect("projects:devis_list")

    except Exception as e:
        messages.error(request, f"Erreur lors de l'archivage: {str(e)}")
        return redirect("projects:devis_detail", pk=pk)


@login_required
def devis_pdf(request, pk):
    """
    View para gerar PDF do devis
    """
    try:
        if request.user.is_staff:
            devis = get_object_or_404(Devis, pk=pk)
        else:
            devis = get_object_or_404(Devis, pk=pk, project__user=request.user)

        # Gerar PDF usando reportlab ou weasyprint
        from django.http import HttpResponse
        from django.template.loader import render_to_string

        # Renderizar template PDF
        html_content = render_to_string(
            "projects/devis_pdf.html",
            {
                "devis": devis,
                "project": devis.project,
            },
        )

        # Se usar weasyprint:
        # import weasyprint
        # pdf = weasyprint.HTML(string=html_content).write_pdf()

        # Por enquanto, retornar HTML (implementar PDF depois)
        response = HttpResponse(html_content, content_type="text/html")
        response["Content-Disposition"] = (
            f'inline; filename="devis_{devis.reference}.html"'
        )

        return response

    except Exception as e:
        messages.error(request, f"Erreur lors de la génération du PDF: {str(e)}")
        return redirect("projects:devis_detail", pk=pk)


# ================================
# VIEW PARA RESPONDER DEVIS (CLIENTE)
# ================================


@login_required
@require_POST
@csrf_protect
def devis_respond(request, pk):
    """
    View para cliente responder a um devis
    """
    try:
        devis = get_object_or_404(Devis, pk=pk, project__user=request.user)

        if devis.status != "envoye":
            messages.error(
                request, "Ce devis ne peut pas être modifié dans son état actuel."
            )
            return redirect("projects:devis_detail", pk=pk)

        if devis.is_expired:
            messages.error(request, "Ce devis a expiré.")
            return redirect("projects:devis_detail", pk=pk)

        if request.method == "POST":
            action = request.POST.get("action")

            if action == "accept":
                return devis_accept(request, pk)
            elif action == "refuse":
                return devis_refuse(request, pk)
            elif action == "request_modification":
                # Implementar lógica para solicitar modificação
                modification_comment = request.POST.get("modification_comment", "")

                if modification_comment:
                    # Salvar comentário e notificar equipe
                    # DevisComment.objects.create(...)
                    messages.success(
                        request, "Votre demande de modification a été envoyée."
                    )
                else:
                    messages.error(
                        request, "Veuillez ajouter un commentaire pour la modification."
                    )

        context = {
            "devis": devis,
            "project": devis.project,
            "can_respond": devis.status == "envoye" and not devis.is_expired,
        }

        return render(request, "projects/devis_respond.html", context)

    except Exception as e:
        messages.error(request, f"Erreur: {str(e)}")
        return redirect("projects:devis_detail", pk=pk)


class DevisDeleteView(LoginRequiredMixin, DeleteView):
    """
    View para deletar devis com validações rigorosas
    """

    model = Devis
    template_name = "projects/devis_delete.html"
    context_object_name = "devis"

    def get_queryset(self):
        """Filtrar devis baseado nas permissões do usuário"""
        if self.request.user.is_staff:
            return Devis.objects.all()
        return Devis.objects.filter(project__user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        devis = self.get_object()

        # Verificar se pode ser deletado
        context["can_be_deleted"] = devis.can_be_deleted()

        # Informações sobre impacto da exclusão
        context["impact_info"] = {
            "is_sent": devis.status != "brouillon",
            "is_accepted": devis.status == "accepte",
            "is_expired": devis.is_expired() if hasattr(devis, "is_expired") else False,
            "has_items": devis.items.count() if hasattr(devis, "items") else 0,
            "client_email": devis.project.user.email,
            "financial_amount": devis.total,
        }

        # Razões de bloqueio
        context["blocking_reasons"] = []
        if devis.status == "accepte":
            context["blocking_reasons"].append("Devis accepté par le client")
        if devis.status == "en_cours":
            context["blocking_reasons"].append("Projet en cours d'exécution")

        return context

    def dispatch(self, request, *args, **kwargs):
        """Verificar permissões antes de processar"""
        devis = self.get_object()

        # Apenas staff pode deletar devis enviados
        if devis.status != "brouillon" and not request.user.is_staff:
            messages.error(
                request,
                "Seuls les administrateurs peuvent supprimer des devis envoyés.",
            )
            return redirect("projects:devis_detail", pk=devis.pk)

        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """Override delete com validações e audit trail"""
        devis = self.get_object()

        # Verificar se pode ser deletado
        if not devis.can_be_deleted():
            messages.error(
                request, "Ce devis ne peut pas être supprimé en raison de son statut."
            )
            return redirect("projects:devis_detail", pk=devis.pk)

        # Validações especiais para devis aceitos
        if devis.status == "accepte" and not request.user.is_superuser:
            messages.error(
                request,
                "Les devis acceptés ne peuvent être supprimés que par un super-administrateur.",
            )
            return redirect("projects:devis_detail", pk=devis.pk)

        # Obter informações para logging
        devis_reference = devis.reference
        devis_title = devis.title
        project_title = devis.project.title
        deletion_reason = request.POST.get("deletion_reason", "Non spécifiée")
        deletion_comment = request.POST.get("deletion_comment", "")

        try:
            # Criar log de auditoria antes da exclusão
            self._create_deletion_audit_log(
                devis, deletion_reason, deletion_comment, request.user
            )

            # Notificar equipe para devis críticos
            if devis.status in ["accepte", "envoye"]:
                self._send_critical_deletion_notification(devis, request.user)

            # Deletar devis
            response = super().delete(request, *args, **kwargs)

            messages.success(
                request,
                f"Devis '{devis_title}' ({devis_reference}) supprimé avec succès.",
            )

            return response

        except Exception as e:
            messages.error(request, f"Erreur lors de la suppression: {str(e)}")
            return redirect("projects:devis_detail", pk=devis.pk)

    def _create_deletion_audit_log(self, devis, reason, comment, user):
        """Criar log de auditoria para a exclusão"""
        try:
            # Se você tiver um modelo de AuditLog
            # AuditLog.objects.create(
            #     action='DEVIS_DELETED',
            #     object_type='Devis',
            #     object_id=str(devis.pk),
            #     object_repr=str(devis),
            #     user=user,
            #     changes={
            #         'deleted_devis': {
            #             'reference': devis.reference,
            #             'title': devis.title,
            #             'status': devis.status,
            #             'total': float(devis.total),
            #             'project': devis.project.title,
            #             'deletion_reason': reason,
            #             'deletion_comment': comment,
            #         }
            #     }
            # )

            # Por enquanto, usar logging do Django
            import logging

            logger = logging.getLogger("projects.devis.deletion")
            logger.warning(
                f"DEVIS DELETED - Reference: {devis.reference}, "
                f"User: {user.username}, Reason: {reason}, "
                f"Comment: {comment}"
            )
        except Exception as e:
            print(f"Erro ao criar audit log: {e}")

    def _send_critical_deletion_notification(self, devis, user):
        """Enviar notificação para exclusões críticas"""
        try:
            # Implementar notificação por email
            # send_mail(
            #     subject=f"ALERTE: Suppression de devis critique - {devis.reference}",
            #     message=f"Le devis {devis.reference} ({devis.status}) a été supprimé par {user.get_full_name()}",
            #     from_email=settings.DEFAULT_FROM_EMAIL,
            #     recipient_list=[settings.ADMIN_EMAIL],
            # )
            pass
        except Exception as e:
            print(f"Erro ao enviar notificação: {e}")

    def get_success_url(self):
        """Rediriger vers liste de devis après suppression"""
        return reverse_lazy("projects:devis_list")
