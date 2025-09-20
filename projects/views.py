from django.forms import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from .models import Project, Devis, DevisLine, Product, DevisHistory, Status
from .forms import (
    ProjectStep1Form,
    ProjectStep2Form,
    ProjectStep3Form,
    ProjectForm,
    ProduitForm,
    DevisLigneForm,
)
import json
from decimal import Decimal
from datetime import datetime, date, timedelta
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.colors import Color
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse, HttpResponse, Http404
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator

from django.views.decorators.http import require_http_methods

from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.conf import settings
import logging
from accounts.models import AccountType

logger = logging.getLogger(__name__)
User = get_user_model()


def is_client(user):
    """Verifica se o usuário é um cliente."""
    return (
        user.is_authenticated
        and hasattr(user, "account_type")
        and user.account_type == AccountType.CLIENT
    )


def is_collaborator(user):
    """Verifica se o usuário é um colaborador."""
    return (
        user.is_authenticated
        and hasattr(user, "account_type")
        and user.account_type == AccountType.COLLABORATOR
    )


def is_admin(user):
    """Verifica se o usuário é um administrador."""
    return (
        user.is_authenticated
        and hasattr(user, "account_type")
        and user.account_type == AccountType.ADMINISTRATOR
    )


def is_staff(user):
    """Verifica se o usuário é staff."""
    return user.is_authenticated and user.is_staff


def can_access_products_devis(user):
    """Verifica se o usuário pode acessar produtos e devis."""
    return (
        user.is_authenticated
        and hasattr(user, "account_type")
        and user.account_type in [AccountType.COLLABORATOR, AccountType.ADMINISTRATOR]
    )


# def can_edit_project(user, project):
#     """Verifica se o usuário pode editar o projeto."""
#     return user == project.user or user.is_staff


# Fonctions utilitaires pour la gestion des Decimal dans les sessions
def serialize_form_data(data):
    """Convertit les objets Decimal et date en format JSON serializable"""
    serialized = {}
    for key, value in data.items():
        if isinstance(value, Decimal):
            serialized[key] = str(value)
        elif isinstance(value, (date, datetime)):
            serialized[key] = (
                value.isoformat() if hasattr(value, "isoformat") else str(value)
            )
        else:
            serialized[key] = value
    return serialized


def deserialize_form_data(data, form_class):
    """Convertit les données de session vers le format attendu par le formulaire"""
    if not data:
        return {}

    deserialized = {}
    # Obtenir les champs du modèle pour identifier les types
    model_fields = {
        field.name: field for field in form_class.Meta.model._meta.get_fields()
    }

    for key, value in data.items():
        if key in model_fields:
            field = model_fields[key]
            # Conversion pour DecimalField
            if hasattr(field, "decimal_places") and value:
                try:
                    deserialized[key] = Decimal(str(value))
                except (ValueError, TypeError):
                    deserialized[key] = value
            # Conversion pour DateField
            elif hasattr(field, "null") and isinstance(value, str) and value:
                try:
                    if "date" in field.__class__.__name__.lower():
                        deserialized[key] = (
                            datetime.fromisoformat(value).date()
                            if "T" in value
                            else datetime.strptime(value, "%Y-%m-%d").date()
                        )
                    else:
                        deserialized[key] = value
                except (ValueError, TypeError):
                    deserialized[key] = value
            else:
                deserialized[key] = value
        else:
            deserialized[key] = value

    return deserialized


# ====
# VIEWS DE DASHBOARD
# ====


@login_required
def dashboard_projects(request):
    """
    Dashboard principal de projetos para o usuário.
    """
    user = request.user

    # Estatísticas básicas
    projects = Project.objects.filter(created_by=user)
    total_projects = projects.count()
    active_projects = projects.exclude(
        status__in=[Status.COMPLETED, Status.CANCELLED]
    ).count()
    completed_projects = projects.filter(status=Status.COMPLETED).count()

    # Projetos recentes
    recent_projects = projects.order_by("-created_at")[:5]

    # Devis pendentes
    pending_devis = Devis.objects.filter(
        project__created_by=user, status__in=[Devis.Status.SENT, Devis.Status.VIEWED]
    ).order_by("-date_created")[:5]

    # Estatísticas por status
    status_stats = {}
    for status, label in Status.choices:
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


# @user_passes_test(is_staff)
# def admin_dashboard(request):
#     """
#     Dashboard administrativo.
#     """
#     # Estatísticas gerais
#     total_projects = Project.objects.count()
#     total_users = User.objects.filter(is_staff=False).count()
#     total_devis = Devis.objects.count()
#     total_products = Product.objects.filter(is_active=True).count()

#     # Projetos por status
#     projects_by_status = {}
#     for status, label in Project.Status.choices:
#         count = Project.objects.filter(status=status).count()
#         if count > 0:
#             projects_by_status[label] = count

#     # Devis por status
#     devis_by_status = {}
#     for status, label in Devis.Status.choices:
#         count = Devis.objects.filter(status=status).count()
#         if count > 0:
#             devis_by_status[label] = count

#     # Projetos recentes
#     recent_projects = Project.objects.select_related("user").order_by("-created_at")[
#         :10
#     ]

#     # Devis pendentes de resposta
#     pending_devis = (
#         Devis.objects.select_related("project", "project__user")
#         .filter(status__in=[Devis.Status.SENT, Devis.Status.VIEWED])
#         .order_by("-date_created")[:10]
#     )

#     context = {
#         "total_projects": total_projects,
#         "total_users": total_users,
#         "total_devis": total_devis,
#         "total_products": total_products,
#         "projects_by_status": projects_by_status,
#         "devis_by_status": devis_by_status,
#         "recent_projects": recent_projects,
#         "pending_devis": pending_devis,
#     }

#     return render(request, "projects/admin_dashboard.html", context)


# ====
# VIEWS DE PROJETOS
# ====


# PROJETS VIEWS
# Atualizar a função projet_list:
@login_required
def projet_list(request):
    """
    Lista de projetos do usuário com filtros e paginação.
    """
    # Base queryset
    if request.user.is_staff:
        projects = Project.objects.all()
    else:
        projects = Project.objects.filter(created_by=request.user)

    # Aplicar filtros
    search = request.GET.get("search", "").strip()
    if search:
        projects = projects.filter(
            Q(title__icontains=search)
            | Q(description__icontains=search)
            | Q(ville__icontains=search)
            | Q(reference__icontains=search)
        )

    status = request.GET.get("status", "").strip()
    if status:
        projects = projects.filter(status=status)

    project_type = request.GET.get("project_type", "").strip()
    if project_type:
        projects = projects.filter(project_type=project_type)

    priority = request.GET.get("priority", "").strip()
    if priority:
        projects = projects.filter(priority=priority)

    # Filtros de data
    date_from = request.GET.get("date_from", "").strip()
    if date_from:
        try:
            date_from_parsed = datetime.strptime(date_from, "%Y-%m-%d").date()
            projects = projects.filter(created_at__date__gte=date_from_parsed)
        except ValueError:
            pass

    date_to = request.GET.get("date_to", "").strip()
    if date_to:
        try:
            date_to_parsed = datetime.strptime(date_to, "%Y-%m-%d").date()
            projects = projects.filter(created_at__date__lte=date_to_parsed)
        except ValueError:
            pass

    # Ordenação
    ordering = request.GET.get("ordering", "-created_at")
    valid_orderings = [
        "created_at",
        "-created_at",
        "title",
        "-title",
        "priority",
        "-priority",
        "surface_totale",
        "-surface_totale",
        "updated_at",
        "-updated_at",
    ]
    if ordering in valid_orderings:
        projects = projects.order_by(ordering)
    else:
        projects = projects.order_by("-created_at")

    # ===== CALCULAR ESTATÍSTICAS =====
    user_projects = (
        Project.objects.filter(created_by=request.user)
        if not request.user.is_staff
        else Project.objects.all()
    )

    # Contagens por status
    total_projects = user_projects.count()

    # Projetos ativos (em curso, aceitos, etc.)
    active_statuses = ["en_cours", "devis_accepte"]
    active_projects = user_projects.filter(status__in=active_statuses).count()

    # Projetos pendentes (aguardando ação)
    pending_statuses = ["soumis", "en_examen", "devis_demande", "devis_envoye"]
    pending_projects = user_projects.filter(status__in=pending_statuses).count()

    # Projetos terminados
    completed_projects = user_projects.filter(status="termine").count()

    # Projetos por status individual
    projects_by_status = {
        "brouillon": user_projects.filter(status="brouillon").count(),
        "soumis": user_projects.filter(status="soumis").count(),
        "en_examen": user_projects.filter(status="en_examen").count(),
        "devis_demande": user_projects.filter(status="devis_demande").count(),
        "devis_envoye": user_projects.filter(status="devis_envoye").count(),
        "devis_accepte": user_projects.filter(status="devis_accepte").count(),
        "en_cours": user_projects.filter(status="en_cours").count(),
        "termine": user_projects.filter(status="termine").count(),
    }

    # Paginação
    paginator = Paginator(projects, 12)  # 12 projetos por página
    page_number = request.GET.get("page")
    try:
        page_obj = paginator.get_page(page_number)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.get_page(1)

    # Data para filtro rápido (última semana)
    last_week = timezone.now() - timedelta(days=7)

    context = {
        "projects": page_obj,
        "page_obj": page_obj,
        "paginator": paginator,
        "is_paginated": page_obj.has_other_pages(),
        # === ESTATÍSTICAS ===
        "total_projects": total_projects,
        "active_projects": active_projects,
        "pending_projects": pending_projects,
        "completed_projects": completed_projects,
        "projects_by_status": projects_by_status,
        # Dados para filtros
        "search": search,
        "status": status,
        "project_type": project_type,
        "priority": priority,
        "date_from": date_from,
        "date_to": date_to,
        "ordering": ordering,
        "last_week": last_week,
        # Para debug
        "debug_stats": (
            {
                "total": total_projects,
                "active": active_projects,
                "pending": pending_projects,
                "completed": completed_projects,
            }
            if settings.DEBUG
            else None
        ),
    }

    return render(request, "projects/project_list.html", context)


@login_required
def projet_create_step1(request):
    """Création projet - Étape 1"""
    if request.method == "POST":
        form = ProjectStep1Form(request.POST)
        if form.is_valid():
            # Sérialiser les données pour éviter les erreurs JSON avec les Decimal
            serialized_data = serialize_form_data(form.cleaned_data)
            request.session["projet_step1"] = serialized_data
            return redirect("projects:projet_create_step2")
    else:
        # Récupérer et désérialiser les données de session si disponibles
        session_data = request.session.get("projet_step1", {})
        initial_data = deserialize_form_data(session_data, ProjectStep1Form)
        form = ProjectStep1Form(initial=initial_data)

    return render(
        request, "projects/projet_create_step1.html", {"form": form, "step": 1}
    )


@login_required
def projet_create_step2(request):
    """Création projet - Étape 2"""
    if "projet_step1" not in request.session:
        messages.error(request, "Veuillez commencer par la première étape.")
        return redirect("projects:projet_create_step1")

    if request.method == "POST":
        form = ProjectStep2Form(request.POST)
        if form.is_valid():
            # Sérialiser les données pour éviter les erreurs JSON
            serialized_data = serialize_form_data(form.cleaned_data)
            request.session["projet_step2"] = serialized_data
            return redirect("projects:projet_create_step3")
    else:
        # Récupérer et désérialiser les données de session si disponibles
        session_data = request.session.get("projet_step2", {})
        initial_data = deserialize_form_data(session_data, ProjectStep2Form)
        form = ProjectStep2Form(initial=initial_data)

    return render(
        request, "projects/projet_create_step2.html", {"form": form, "step": 2}
    )


@login_required
def projet_create_step3(request):
    """Création projet - Étape 3 et finalisation"""
    if "projet_step1" not in request.session or "projet_step2" not in request.session:
        messages.error(request, "Veuillez compléter toutes les étapes précédentes.")
        return redirect("projects:projet_create_step1")

    if request.method == "POST":
        form = ProjectStep3Form(request.POST)
        if form.is_valid():
            # Récupérer et désérialiser toutes les données des étapes précédentes
            step1_data = deserialize_form_data(
                request.session["projet_step1"], ProjectStep1Form
            )
            step2_data = deserialize_form_data(
                request.session["projet_step2"], ProjectStep2Form
            )
            step3_data = serialize_form_data(form.cleaned_data)
            step3_data = deserialize_form_data(step3_data, ProjectStep3Form)

            # Combiner toutes les données
            projet_data = {}
            projet_data.update(step1_data)
            projet_data.update(step2_data)
            projet_data.update(step3_data)

            # Ajouter l'utilisateur connecté
            projet_data["created_by"] = request.user

            # Conversion des dates si nécessaire
            for field_name in ["date_debut_souhaitee", "date_fin_souhaitee"]:
                if field_name in projet_data and isinstance(
                    projet_data[field_name], str
                ):
                    try:
                        if projet_data[field_name]:
                            projet_data[field_name] = datetime.strptime(
                                projet_data[field_name], "%Y-%m-%d"
                            ).date()
                        else:
                            projet_data[field_name] = None
                    except (ValueError, TypeError):
                        projet_data[field_name] = None

            projet = Project.objects.create(**projet_data)

            # Nettoyer la session
            for key in ["projet_step1", "projet_step2", "projet_step3"]:
                if key in request.session:
                    del request.session[key]

            messages.success(request, f'Projet "{projet.title}" créé avec succès !')
            return redirect("projects:projet_detail", pk=projet.pk)
    else:
        # Récupérer et désérialiser les données de session si disponibles
        session_data = request.session.get("projet_step3", {})
        initial_data = deserialize_form_data(session_data, ProjectStep3Form)
        form = ProjectStep3Form(initial=initial_data)

    return render(
        request, "projects/projet_create_step3.html", {"form": form, "step": 3}
    )


@login_required
def projet_detail(request, pk):
    """Détail d'un projet"""
    projet = get_object_or_404(Project, pk=pk)

    # Tratar POST requests para ações
    if request.method == "POST":
        action = request.POST.get("action")

        if action == "update_status" and request.user.is_staff:
            new_status = request.POST.get("status")
            notes_internes = request.POST.get("notes_internes", "")

            if new_status and new_status != projet.status:
                projet.status = new_status
                if notes_internes:
                    projet.notes_internes = notes_internes
                projet.save()

                messages.success(
                    request, f"Statut mis à jour vers: {projet.get_status_display()}"
                )
                return redirect("projects:projet_detail", pk=projet.pk)

        elif action == "request_devis":
            # Lógica para solicitar devis
            if projet.status in ["soumis", "en_examen"]:
                projet.status = "devis_demande"
                projet.save()
                messages.success(request, "Devis demandé avec succès!")
            else:
                messages.error(
                    request, "Impossible de demander un devis pour ce projet."
                )

            return redirect("projects:projet_detail", pk=projet.pk)

    # Vérifier les permissions d'accès
    can_view = request.user.is_staff or projet.created_by == request.user

    if not can_view:
        messages.error(request, "Vous n'avez pas accès à ce projet.")
        return redirect("projects:projet_list")

    devis_list = projet.devis.all()

    # Usar Status enum:
    can_request_devis = projet.created_by == request.user and projet.status in [
        Status.SUBMITTED,
        Status.UNDER_REVIEW,
    ]

    can_edit = request.user.is_staff or (
        projet.created_by == request.user and projet.status == Status.DRAFT
    )

    is_staff = request.user.is_staff

    context = {
        "project": projet,
        "projet": projet,
        "devis_list": devis_list,
        "can_request_devis": can_request_devis,
        "can_edit": can_edit,
        "is_staff": is_staff,
    }
    return render(request, "projects/project_detail.html", context)


# ATUALIZAR a função projet_update:
@login_required
def projet_update(request, pk):
    """
    Edição de projeto.
    """
    try:
        project = get_object_or_404(Project, pk=pk, created_by=request.user)
    except ValidationError:
        messages.error(request, "ID de projeto inválido.")
        return redirect("projects:projet_list")

    # Verificar se o usuário pode editar este projeto
    if not request.user.is_staff and project.status not in ["brouillon"]:
        messages.warning(
            request, "Ce projet ne peut plus être modifié car il a été soumis."
        )
        return redirect("projects:projet_detail", pk=project.pk)

    if request.method == "POST":
        # Verificar se é auto-save
        if request.POST.get("auto_save"):
            # Auto-save silencioso para brouillons
            if project.status == "brouillon":
                form = ProjectForm(request.POST, instance=project, user=request.user)
                if form.is_valid():
                    form.save()
                    return JsonResponse({"status": "success"})
                return JsonResponse({"status": "error", "errors": form.errors})

        # Verificar se é submissão do projeto
        if "submit_project" in request.POST:
            form = ProjectForm(request.POST, instance=project, user=request.user)
            if form.is_valid():
                updated_project = form.save(commit=False)
                updated_project.status = "soumis"  # Mudar status para soumis
                updated_project.save()
                messages.success(
                    request,
                    f"Le projet '{updated_project.title}' a été soumis avec succès.",
                )
                return redirect("projects:projet_detail", pk=updated_project.pk)
        else:
            # Salvamento normal
            form = ProjectForm(request.POST, instance=project, user=request.user)
            if form.is_valid():
                try:
                    updated_project = form.save()
                    messages.success(
                        request,
                        f"Le projet '{updated_project.title}' a été mis à jour avec succès.",
                    )
                    return redirect("projects:projet_detail", pk=updated_project.pk)
                except Exception as e:
                    logger.error(f"Erreur lors de la mise à jour du projet {pk}: {e}")
                    messages.error(
                        request,
                        "Une erreur est survenue lors de la mise à jour. Veuillez réessayer.",
                    )
            else:
                messages.error(
                    request, "Veuillez corriger les erreurs dans le formulaire."
                )
    else:
        form = ProjectForm(instance=project, user=request.user)

    context = {
        "form": form,
        "project": project,
        "is_staff": request.user.is_staff,
        "can_edit": request.user.is_staff or project.status == "brouillon",
    }
    return render(request, "projects/project_edit.html", context)


# ====
# DELETE VIEWS - PROJETOS E DEVIS
# ====


def projet_delete(request, pk):
    """Suppression d'un projet"""
    projet = get_object_or_404(Project, pk=pk)
    if request.method == "POST":
        projet.delete()
        messages.success(request, "Projet supprimé avec succès !")
        return redirect("projects:projet_list")

    return render(request, "projects/projet_delete.html", {"projet": projet})


def projet_create_devis(request, pk):
    """Créer un devis pour un projet"""
    projet = get_object_or_404(Project, pk=pk)

    if request.method == "POST":
        # Créer le devis de base
        devis = Devis.objects.create(
            project=projet,
            titre=f"Devis pour {projet.title}",
            description=f"Devis automatique généré pour le projet {projet.reference}",
            terms_conditions="Devis valable 30 jours. Paiement à 30 jours fin de mois.",
        )

        messages.success(request, f"Devis {devis.reference} créé avec succès !")
        return redirect("projects:devis_detail", pk=devis.pk)

    return render(request, "projects/devis_create.html", {"projet": projet})


# PRODUITS VIEWS
@login_required
@user_passes_test(can_access_products_devis, login_url="/accounts/login/")
def produit_list(request):
    """Liste des produits avec recherche"""
    produits = Product.objects.all()

    search = request.GET.get("search", "")
    if search:
        produits = produits.filter(
            Q(name__icontains=search)
            | Q(code__icontains=search)
            | Q(description__icontains=search)
        )

    type_filter = request.GET.get("type", "")
    if type_filter:
        produits = produits.filter(type_produit=type_filter)

    active_filter = request.GET.get("active", "")
    if active_filter == "true":
        produits = produits.filter(is_active=True)
    elif active_filter == "false":
        produits = produits.filter(is_active=False)

    context = {
        "produits": produits,
        "search": search,
        "type_filter": type_filter,
        "active_filter": active_filter,
    }
    return render(request, "projects/produit_list.html", context)


@login_required
@user_passes_test(can_access_products_devis, login_url="/accounts/login/")
def produit_create(request):
    """Créer un nouveau produit."""

    print("=" * 80)
    print("🚨 PRODUIT_CREATE CHAMADA!")
    print(f"📝 Method: {request.method}")
    print(f"👤 User: {request.user}")
    print(f"📧 User email: {request.user.email}")
    print(f"🔐 User authenticated: {request.user.is_authenticated}")
    print(f"📊 POST data: {dict(request.POST)}")
    print(f"📊 GET data: {dict(request.GET)}")
    print("=" * 80)

    if request.method == "POST":
        print("🔥 PROCESSANDO POST REQUEST")
        print(f"📝 POST keys: {list(request.POST.keys())}")
        print(f"📝 CSRF token present: {'csrfmiddlewaretoken' in request.POST}")

        try:
            print("🏗️ Criando formulário com dados POST...")
            form = ProduitForm(request.POST)
            print(f"✅ Formulário criado: {form}")

            print("🔍 Verificando se formulário é válido...")
            is_valid = form.is_valid()
            print(f"📊 Form is_valid: {is_valid}")

            if is_valid:
                print("🎉 FORMULÁRIO VÁLIDO!")
                print(f"📊 Cleaned data: {form.cleaned_data}")

                try:
                    print("💾 Tentando salvar produto...")
                    produit = form.save()
                    print(f"🎉 PRODUTO SALVO COM SUCESSO: {produit}")
                    print(f"🆔 ID do produto: {produit.pk}")
                    print(f"📝 Nome do produto: {produit.name}")

                    print("📨 Adicionando mensagem de sucesso...")
                    messages.success(
                        request, f"Produit '{produit.name}' créé avec succès!"
                    )

                    print("🔄 Fazendo redirect...")
                    redirect_url = reverse(
                        "projects:produit_detail", kwargs={"pk": produit.pk}
                    )
                    print(f"🔗 Redirect URL: {redirect_url}")

                    return redirect("projects:produit_detail", pk=produit.pk)

                except Exception as save_error:
                    print(f"💥 ERRO AO SALVAR: {save_error}")
                    print(f"💥 Tipo do erro: {type(save_error)}")
                    import traceback

                    traceback.print_exc()
                    messages.error(request, f"Erreur lors de la création: {save_error}")

            else:
                print("❌ FORMULÁRIO INVÁLIDO!")
                print(f"💥 Erros do formulário: {form.errors}")
                print(f"💥 Erros por campo:")
                for field_name, field_errors in form.errors.items():
                    print(f"   🔸 {field_name}: {field_errors}")

                messages.error(request, "Veuillez corriger les erreurs du formulaire.")

        except Exception as form_error:
            print(f"💥 ERRO AO CRIAR FORMULÁRIO: {form_error}")
            import traceback

            traceback.print_exc()
            form = ProduitForm()
            messages.error(request, f"Erreur: {form_error}")

    else:
        print("📝 GET REQUEST - Criando formulário vazio")
        try:
            form = ProduitForm()
            print(f"✅ Formulário vazio criado: {form}")
        except Exception as e:
            print(f"💥 ERRO ao criar formulário vazio: {e}")
            form = None

    print(f"🎬 Renderizando template com contexto...")
    print(f"📊 Form fields: {list(form.fields.keys()) if form else 'FORM IS NONE'}")

    context = {
        "form": form,
        "debug": True,
    }

    print(f"📄 Context: {context}")
    print("🎬 Chamando render...")

    try:
        response = render(request, "projects/produit_create.html", context)
        print(f"✅ Render executado com sucesso")
        print(f"📊 Response status: {response.status_code}")
        return response
    except Exception as render_error:
        print(f"💥 ERRO NO RENDER: {render_error}")
        import traceback

        traceback.print_exc()
        raise


@login_required
@user_passes_test(can_access_products_devis, login_url="/accounts/login/")
def produit_detail(request, pk):
    """Détail d'un produit"""
    produit = get_object_or_404(Product, pk=pk)
    return render(request, "projects/produit_detail.html", {"produit": produit})


@login_required
@user_passes_test(can_access_products_devis, login_url="/accounts/login/")
def produit_update(request, pk):
    """Modification d'un produit"""
    produit = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = ProduitForm(request.POST, instance=produit)
        if form.is_valid():
            form.save()
            messages.success(request, "Produit modifié avec succès !")
            return redirect("projects:produit_detail", pk=produit.pk)
    else:
        form = ProduitForm(instance=produit)

    return render(
        request, "projects/produit_update.html", {"form": form, "produit": produit}
    )


@login_required
@user_passes_test(can_access_products_devis, login_url="/accounts/login/")
def produit_delete(request, pk):
    """Suppression d'un produit"""
    produit = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        produit.delete()
        messages.success(request, "Produit supprimé avec succès !")
        return redirect("projects:produit_list")

    return render(request, "projects/produit_delete.html", {"produit": produit})


# ====
# VIEWS DE DEVIS
# ====


@login_required
@user_passes_test(can_access_products_devis, login_url="/accounts/login/")
def devis_list(request):
    """Liste des devis"""
    devis_queryset = Devis.objects.select_related("project").all()

    search = request.GET.get("search", "")
    if search:
        devis_queryset = devis_queryset.filter(
            Q(reference__icontains=search)
            | Q(titre__icontains=search)
            | Q(project__title__icontains=search)
        )

    status_filter = request.GET.get("status", "")
    if status_filter:
        devis_queryset = devis_queryset.filter(status=status_filter)

    context = {
        "devis_list": devis_queryset,
        "search": search,
        "status_filter": status_filter,
    }
    return render(request, "projects/devis_list.html", context)


@login_required
@user_passes_test(can_access_products_devis, login_url="/accounts/login/")
def devis_detail(request, pk):
    """Détail d'un devis avec possibilité d'ajouter des lignes"""
    devis = get_object_or_404(Devis, pk=pk)
    lignes = devis.lignes.all()

    if request.method == "POST":
        # Traitement d'ajout de ligne
        produit_id = request.POST.get("produit")
        quantity = request.POST.get("quantity")
        price_unit = request.POST.get("price_unit")
        description = request.POST.get("description", "")

        if produit_id and quantity and price_unit:
            produit = get_object_or_404(Product, pk=produit_id)
            DevisLine.objects.create(
                devis=devis,
                produit=produit,
                description=description or produit.name,
                quantity=float(quantity),
                price_unit=float(price_unit),
            )
            messages.success(request, "Ligne ajoutée au devis !")
            return redirect("projects:devis_detail", pk=devis.pk)

    # Récupérer les produits actifs pour le formulaire
    produits = Product.objects.filter(is_active=True).order_by("name")

    context = {
        "devis": devis,
        "lignes": lignes,
        "produits": produits,
    }
    return render(request, "projects/devis_detail.html", context)


@login_required
@user_passes_test(can_access_products_devis, login_url="/accounts/login/")
def devis_delete(request, pk):
    """Suppression d'un devis"""
    devis = get_object_or_404(Devis, pk=pk)
    if request.method == "POST":
        projet_pk = devis.project.pk
        devis.delete()
        messages.success(request, "Devis supprimé avec succès !")
        return redirect("projects:projet_detail", pk=projet_pk)

    return render(request, "projects/devis_delete.html", {"devis": devis})


def devis_pdf(request, pk):
    """Génération PDF d'un devis à partir de template HTML"""
    devis = get_object_or_404(Devis, pk=pk)

    # Contexte pour le template
    context = {
        "devis": devis,
        "hoje": datetime.now().strftime("%d/%m/%Y"),
        "empresa": {
            "nome": devis.company_name,
            "endereco": devis.company_address,
            "codigo_postal": devis.company_postal_code,
            "cidade": devis.company_city,
            "telefone": devis.company_phone,
            "email": devis.company_email,
        },
        "cliente": {
            "nome": devis.project.contact_nom,
            "endereco": devis.project.adresse_travaux,
            "codigo_postal": devis.project.code_postal,
            "cidade": devis.project.ville,
            "telefone": devis.project.contact_telephone or "N/A",
        },
    }

    try:
        # Renderizar template HTML
        html_string = render_to_string("projects/devis_pdf.html", context)

        # Criar resposta HTTP
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = (
            f'inline; filename="devis_{devis.reference}.pdf"'
        )

        # Gerar PDF com xhtml2pdf
        pisa_status = pisa.CreatePDF(html_string, dest=response)

        # Verificar se houve erro
        if pisa_status.err:
            return HttpResponse("Erro na geração do PDF", status=500)

        return response

    except Exception as e:
        import logging

        logging.error(f"Erro geração PDF devis {pk}: {str(e)}")
        return HttpResponse(
            f"Erro na geração do PDF: {str(e)}", status=500, content_type="text/plain"
        )


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
        if not devis.lines.exists():
            messages.error(
                request, "Le devis doit contenir au moins un item avant d'être envoyé."
            )
            return redirect("projects:devis_edit", pk=pk)

        # Mettre à jour le status et la date d'envoi
        devis.status = "envoye"
        devis.date_sent = timezone.now()
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


# ====
# VIEWS DE PRODUTOS (ADMIN)
# ====
