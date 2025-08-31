from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.views.decorators.http import require_http_methods, require_POST
from django.http import JsonResponse, HttpResponseForbidden
from django.urls import reverse, reverse_lazy
from django.core.mail import send_mail
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Project
from .decorators import can_edit_project
from .models import User, UserProfile, Project
from .forms import (
    UserRegistrationForm,
    UserLoginForm,
    UserProfileForm,
    ProjectForm,
    PasswordResetForm,
)
from .decorators import superuser_required, permission_required, can_edit_project
from .utils import generate_verification_token, export_user_data_to_csv

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.http import JsonResponse
from django.core.serializers import serialize
from django.utils.timezone import localtime
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)
# Autenticação
@csrf_protect
@require_http_methods(["GET", "POST"])
def register_view(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")

    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Aguarda verificação por email
            user.save()
            
            logger.info(f"Novo usuário registrado: {user.email}")

            # Envia email de verificação
            token = generate_verification_token(user)
            verification_url = request.build_absolute_uri(
                reverse("accounts:verify_email", kwargs={"token": token})
            )
            send_mail(
                "Vérifiez votre email",
                f"Cliquez ici pour vérifier votre email: {verification_url}",
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )

            messages.success(
                request, "Compte créé avec succès! Veuillez vérifier votre email."
            )
            return redirect("accounts:login")
    else:
        form = UserRegistrationForm()

    return render(request, "accounts/register.html", {"form": form})


@csrf_protect
@require_http_methods(["GET", "POST"])
def user_login_view(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")

    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = authenticate(request, email=email, password=password)

            if user is not None:
                if user.is_active:
                    login(request, user)
                    next_url = request.GET.get("next", "accounts:dashboard")
                    return redirect(next_url)
                else:
                    messages.error(
                        request, "Compte non vérifié. Veuillez vérifier votre email."
                    )
            else:
                messages.error(request, "Email ou mot de passe invalide.")
    else:
        form = UserLoginForm()

    return render(request, "accounts/login.html", {"form": form})


@login_required
def user_logout_view(request):
    logout(request)
    return redirect("home:home")


@login_required
@require_POST
def ajax_logout_view(request):
    logout(request)
    return JsonResponse({"status": "success"})


# Gerenciamento de Perfil
class ProfileView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = "accounts/profile.html"
    success_url = reverse_lazy("accounts:profile")

    def get_object(self):
        return self.request.user.profile


profile = ProfileView.as_view()


@method_decorator(login_required, name="dispatch")
class DashboardView(ListView):
    template_name = "accounts/dashboard.html"
    context_object_name = "projects"

    def get_queryset(self):
        return Project.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recent_projects"] = self.get_queryset()[:5]
        return context


dashboard = DashboardView.as_view()


# Projetos
@method_decorator(login_required, name="dispatch")
class ProjectListView(ListView):
    template_name = "accounts/project_list.html"
    context_object_name = "projects"

    def get_queryset(self):
        return Project.objects.filter(user=self.request.user)


mes_projets = ProjectListView.as_view()


@method_decorator(login_required, name="dispatch")
class ProjectCreateView(CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "accounts/project_form.html"
    success_url = reverse_lazy("accounts:mes_projets")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


criar_projeto = ProjectCreateView.as_view()


# AJAX Endpoints
@login_required
@require_POST
def upload_avatar(request):
    if "avatar" not in request.FILES:
        return JsonResponse({"error": "Aucune image n'a été fournie"}, status=400)

    profile = request.user.profile
    profile.avatar = request.FILES["avatar"]
    profile.save()

    return JsonResponse(
        {
            "status": "success",
            "message": "Avatar mis à jour avec succès",
            "avatar_url": profile.avatar.url,
        }
    )


@login_required
@require_POST
def remove_avatar(request):
    profile = request.user.profile
    profile.avatar = None
    profile.save()

    return JsonResponse({"status": "success", "message": "Avatar supprimé avec succès"})


@login_required
def get_user_data(request):
    """
    Endpoint AJAX para obter dados do usuário logado.
    Retorna informações básicas do usuário e seu perfil em formato JSON.
    """
    user = request.user
    profile = user.profile

    # Formatação de datas para o formato francês
    date_joined = localtime(user.date_joined).strftime("%d/%m/%Y")
    last_login = (
        localtime(user.last_login).strftime("%d/%m/%Y") if user.last_login else None
    )
    birth_date = (
        profile.date_of_birth.strftime("%d/%m/%Y") if profile.date_of_birth else None
    )

    data = {
        "user": {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "date_joined": date_joined,
            "last_login": last_login,
            "is_active": user.is_active,
            "account_type": user.account_type,
        },
        "profile": {
            "phone": profile.phone,
            "address": profile.address,
            "date_of_birth": birth_date,
            "bio": profile.bio,
            "avatar_url": profile.avatar.url if profile.avatar else None,
        },
        "projects_count": user.projects.count(),
        "active_projects_count": user.projects.filter(status="en_cours").count(),
    }

    # Dados adicionais para profissionais
    if user.account_type == "PROFESSIONAL":
        data["professional"] = {
            "company_name": (
                user.professional.company_name
                if hasattr(user, "professional")
                else None
            ),
            "siret": user.professional.siret if hasattr(user, "professional") else None,
            "experience_years": (
                user.professional.experience_years
                if hasattr(user, "professional")
                else None
            ),
        }

    return JsonResponse(
        {
            "status": "success",
            "data": data,
            "message": "Données utilisateur récupérées avec succès",
        }
    )


# Admin Views
@method_decorator(superuser_required, name="dispatch")
class AdminUserListView(ListView):
    model = User
    template_name = "accounts/admin/user_list.html"
    context_object_name = "users"
    paginate_by = 50

    def get_queryset(self):
        query = self.request.GET.get("q")
        if query:
            return User.objects.filter(
                Q(email__icontains=query)
                | Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
            )
        return User.objects.all()


admin_users_list = AdminUserListView.as_view()


@superuser_required
@require_POST
def admin_toggle_user_status(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = not user.is_active
    user.save()

    return JsonResponse({"status": "success", "is_active": user.is_active})


# Exportação de Dados
@login_required
def export_user_data(request):
    response = export_user_data_to_csv(request.user)
    return response


# Verificação de Email
def verify_email(request, token):
    try:
        user = User.objects.get(verification_token=token)
        if not user.is_active:
            user.is_active = True
            user.verification_token = ""
            user.save()
            messages.success(
                request,
                "Email vérifié avec succès! Vous pouvez maintenant vous connecter.",
            )
        return redirect("accounts:login")
    except User.DoesNotExist:
        messages.error(request, "Lien de vérification invalide ou expiré.")
        return redirect("accounts:register")


@login_required
@permission_required("accounts.view_all_profiles")
def user_list(request):
    # Sua view aqui
    pass


@login_required
@can_edit_project
def editar_projeto(request, projeto_id):
    """
    View para editar um projeto existente.
    Apenas o proprietário do projeto ou um administrador pode editar.
    """
    projeto = get_object_or_404(Project, id=projeto_id)

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=projeto)
        if form.is_valid():
            form.save()
            messages.success(request, "Projet mis à jour avec succès!")
            return redirect("accounts:projeto_detail", projeto_id=projeto.id)
    else:
        form = ProjectForm(instance=projeto)

    context = {
        "form": form,
        "projeto": projeto,
        "title": "Modifier le projet",
        "button_text": "Enregistrer les modifications",
    }

    return render(request, "accounts/edit_projeto.html", context)


@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Atualiza a sessão para manter o usuário logado
            update_session_auth_hash(request, user)
            messages.success(request, "Votre mot de passe a été changé avec succès!")
            return redirect("accounts:profile")
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = PasswordChangeForm(request.user)

    return render(
        request,
        "accounts/change_password.html",
        {"form": form, "title": "Changer le mot de passe"},
    )


@login_required
def delete_account(request):
    if request.method == "POST":
        # Armazena o usuário antes de deletar para mensagem
        user_email = request.user.email

        # Deleta o usuário
        request.user.delete()

        # Faz logout do usuário
        logout(request)

        messages.success(request, "Votre compte a été supprimé avec succès.")
        return redirect("home")

    return render(
        request, "accounts/delete_account.html", {"title": "Supprimer le compte"}
    )


@login_required
def projeto_detail(request, projeto_id):
    """
    View para exibir os detalhes de um projeto específico.
    Apenas o proprietário do projeto ou um administrador pode visualizar.
    """
    projeto = get_object_or_404(Project, id=projeto_id)

    # Verifica se o usuário tem permissão para ver o projeto
    if not (request.user.is_superuser or projeto.user == request.user):
        messages.error(request, "Vous n'avez pas l'autorisation de voir ce projet.")
        return redirect("accounts:mes_projets")

    context = {
        "projeto": projeto,
        "can_edit": request.user.is_superuser or projeto.user == request.user,
        "title": f"Projet: {projeto.type_projet}",
    }

    return render(request, "accounts/projeto_detail.html", context)


@login_required
@can_edit_project
def deletar_projeto(request, projeto_id):
    """
    View para deletar um projeto existente.
    Apenas o proprietário do projeto ou um administrador pode deletar.
    """
    projeto = get_object_or_404(Project, id=projeto_id)

    if request.method == "POST":
        projeto.delete()
        messages.success(request, "Le projet a été supprimé avec succès.")
        return redirect("accounts:mes_projets")

    return render(
        request,
        "accounts/delete_projeto.html",
        {"projeto": projeto, "title": "Supprimer le projet"},
    )


def check_email_exists(request):
    """
    Endpoint AJAX para verificar se um email já está cadastrado.
    Retorna JSON com status e mensagem em francês.
    """
    email = request.GET.get("email", "").lower().strip()

    if not email:
        return JsonResponse(
            {"status": "error", "message": "L'adresse email est requise"}, status=400
        )

    try:
        # Valida o formato do email
        validate_email(email)

        # Verifica se o email já existe
        exists = User.objects.filter(email=email).exists()

        if exists:
            return JsonResponse(
                {"status": "error", "message": "Cette adresse email est déjà utilisée"}
            )
        else:
            return JsonResponse(
                {"status": "success", "message": "Cette adresse email est disponible"}
            )

    except ValidationError:
        return JsonResponse(
            {"status": "error", "message": "Format d'email invalide"}, status=400
        )
