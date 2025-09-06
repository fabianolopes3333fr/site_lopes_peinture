import logging
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView
from django.urls import reverse_lazy, reverse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.tokens import default_token_generator
from utils.emails.sistema_email import (
    send_password_reset_email,
    send_password_changed_email,
)
from django.contrib.auth import (
    update_session_auth_hash,
)
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

from .models import User
from .forms import (
    UserRegistrationForm,
    EmailLoginForm,
    PasswordResetForm,
    PasswordChangeForm,
    PasswordResetConfirmForm,
)


logger = logging.getLogger(__name__)


# ==================== REGISTRO ====================
class RegisterView(CreateView):
    """View de registro com criação automática de perfil e grupos"""

    model = User
    form_class = UserRegistrationForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("accounts:login")

    def dispatch(self, request, *args, **kwargs):
        """Redireciona usuários já autenticados"""
        if request.user.is_authenticated:
            messages.info(request, "Você já está conectado.")
            return redirect("accounts:dashboard")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Processa formulário válido e cria usuário com perfil"""
        try:
            # Salvar usuário (signals criarão perfil e grupos automaticamente)
            user = form.save()

            # Log da criação
            logger.info(
                f"Novo usuário criado: {user.email} - Tipo: {user.account_type}"
            )

            # Mensagem de sucesso
            messages.success(
                self.request,
                f"Compte créé avec succès! Bienvenue {user.first_name}. Vous pouvez maintenant vous connecter.",
            )

            return redirect(self.success_url)

        except Exception as e:
            logger.error(f"Erro ao criar usuário: {e}")
            messages.error(
                self.request,
                "Erreur lors de la création du compte. Veuillez réessayer.",
            )
            return self.form_invalid(form)

    def form_invalid(self, form):
        """Trata formulário inválido"""
        messages.error(
            self.request,
            "Il y a des erreurs dans le formulaire. Veuillez les corriger.",
        )
        return super().form_invalid(form)


register = RegisterView.as_view()


# ==================== LOGIN ====================
@csrf_protect
@require_http_methods(["GET", "POST"])
def user_login(request):
    """✅ CORRIGIDO: View de login por email com redirecionamento inteligente"""

    # Redirecionar se já autenticado
    if request.user.is_authenticated:
        messages.info(request, "Vous êtes déjà connecté.")
        return redirect("accounts:dashboard")

    if request.method == "POST":
        # ✅ CORRIGIDO: Usar EmailLoginForm com logging detalhado
        form = EmailLoginForm(request, data=request.POST)

        # ✅ DEBUG: Log dos dados recebidos
        email_submitted = request.POST.get(
            "username", ""
        )  # O campo é username mas contém email
        logger.debug(f"Tentativa de login para: {email_submitted}")

        if form.is_valid():
            # Fazer login
            user = form.get_user()
            login(request, user)

            # Log do login
            logger.info(f"Login realizado: {user.email} (username: {user.username})")

            # Mensagem de boas-vindas
            messages.success(request, f"Bienvenue, {user.first_name}!")

            # Redirecionamento baseado no tipo de usuário
            next_url = request.GET.get("next")
            if next_url and next_url.startswith("/") and not next_url.startswith("//"):
                return redirect(next_url)

            # Redirecionamento padrão baseado no tipo
            if user.account_type == "ADMINISTRATOR":
                return redirect("admin:index")
            else:
                return redirect("accounts:dashboard")
        else:
            # ✅ DEBUG: Log dos erros do formulário
            logger.warning(
                f"Erro no formulário de login para {email_submitted}: {form.errors}"
            )

            # Formulário inválido
            messages.error(request, "Email ou mot de passe invalide.")
            logger.warning(f"Tentativa de login falhada para: {email_submitted}")
    else:
        # ✅ CORRIGIDO: Usar EmailLoginForm
        form = EmailLoginForm()

    return render(request, "accounts/login.html", {"form": form})


# ==================== LOGOUT ====================
@csrf_protect
@require_http_methods(["GET", "POST"])
def user_logout(request):
    """View de logout com log de segurança"""

    if not request.user.is_authenticated:
        messages.info(request, "Vous n'êtes pas connecté.")
        return redirect("pages:home")

    # Capturar dados antes do logout
    user_email = request.user.email

    # Realizar logout
    logout(request)

    # Log do logout
    logger.info(f"Logout realizado: {user_email}")

    # Mensagem de confirmação
    messages.success(request, "Vous avez été déconnecté avec succès.")

    # Redirecionamento
    next_url = request.POST.get("next") or request.GET.get("next")
    if next_url and next_url.startswith("/") and not next_url.startswith("//"):
        return redirect(next_url)

    return redirect("pages:home")


# ==================== DASHBOARD ====================
@login_required
def dashboard(request):
    """Dashboard principal do usuário"""

    user = request.user

    # Dados do contexto
    context = {
        "user": user,
        "groups": user.groups.all(),
        "profile": getattr(user, "profile", None),
        "account_type_display": user.get_account_type_display(),
        "is_profile_complete": (
            getattr(user.profile, "is_complete", False)
            if hasattr(user, "profile")
            else False
        ),
    }

    # Verificar se perfil existe
    if not hasattr(user, "profile"):
        messages.warning(
            request,
            "Votre profil n'a pas été créé automatiquement. Contactez l'administrateur.",
        )
        logger.warning(f"Usuário {user.email} sem perfil!")

    return render(request, "dashboard/dashboard.html", context)


# ==================== ALTERAÇÃO DE SENHA ====================


@login_required
@csrf_protect
@require_http_methods(["GET", "POST"])
def password_change_view(request):
    """
    View para alteração de senha do usuário logado.
    """
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)

        if form.is_valid():
            form.save()

            # Enviar email de notificação usando o sistema separado
            send_password_changed_email(request.user, request)

            # Atualizar sessão para não deslogar o usuário
            update_session_auth_hash(request, request.user)

            logger.info(f"Senha alterada com sucesso para: {request.user.email}")

            messages.success(
                request, _("Votre mot de passe a été modifié avec succès!")
            )
            return redirect("accounts:profile")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, "accounts/password_change.html", {"form": form})


# ==================== RESET DE SENHA ====================


@csrf_protect
@require_http_methods(["GET", "POST"])
def password_reset_view(request):
    """
    View para solicitação de reset de senha.
    """
    if request.method == "POST":
        form = PasswordResetForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data["email"]

            try:
                user = User.objects.get(email=email, is_active=True)

                # Gerar token de reset
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))

                # URL de reset
                reset_url = request.build_absolute_uri(
                    reverse(
                        "accounts:password_reset_confirm",
                        kwargs={"uidb64": uid, "token": token},
                    )
                )

                # Enviar email usando sistema centralizado
                send_password_reset_email(user, reset_url, request)

                logger.info(f"Email de reset de senha enviado para: {email}")

            except User.DoesNotExist:
                # Por segurança, não revelamos se o email existe ou não
                logger.warning(f"Tentativa de reset para email inexistente: {email}")

            messages.success(
                request,
                _(
                    "Si votre email existe dans notre système, vous recevrez un lien de réinitialisation."
                ),
            )
            return redirect("accounts:password_reset_done")
    else:
        form = PasswordResetForm()

    return render(request, "accounts/password_reset.html", {"form": form})


@csrf_protect
@require_http_methods(["GET", "POST"])
def password_reset_confirm_view(request, uidb64, token):
    """
    View para confirmação e definição de nova senha.
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            form = PasswordResetConfirmForm(user, request.POST)

            if form.is_valid():
                form.save()

                # Enviar email de confirmação usando o sistema separado
                send_password_changed_email(user, request)

                logger.info(f"Senha resetada com sucesso para: {user.email}")

                messages.success(
                    request, _("Votre mot de passe a été réinitialisé avec succès!")
                )
                return redirect("accounts:password_reset_complete")
        else:
            form = PasswordResetConfirmForm(user)

        return render(
            request,
            "accounts/password_reset_confirm.html",
            {"form": form, "validlink": True},
        )
    else:
        logger.warning(f"Token de reset inválido usado: {token}")
        return render(
            request, "accounts/password_reset_confirm.html", {"validlink": False}
        )


@require_http_methods(["GET"])
def password_reset_done_view(request):
    """
    View que mostra mensagem após solicitação de reset de senha.
    """
    return render(request, "accounts/password_reset_done.html")


@require_http_methods(["GET"])
def password_reset_complete_view(request):
    """
    View que confirma que a senha foi resetada com sucesso.
    """
    return render(request, "accounts/password_reset_complete.html")


# ==================== PROFILE ====================
@login_required
def profile(request):
    """View do perfil do usuário"""

    user = request.user

    # Verificar se perfil existe, criar se necessário
    if not hasattr(user, "profile"):
        from profiles.models import Profile

        Profile.objects.create(user=user)
        messages.info(request, "Profil créé automatiquement.")
        logger.info(f"Perfil criado manualmente para {user.email}")

    context = {"user": user, "profile": user.profile, "groups": user.groups.all()}

    return render(request, "accounts/profile.html", context)


# ==================== AJAX VIEWS ====================
@login_required
@require_http_methods(["POST"])
def ajax_logout(request):
    """Logout via AJAX"""

    user_email = request.user.email
    logout(request)

    logger.info(f"Logout AJAX: {user_email}")

    return JsonResponse(
        {
            "status": "success",
            "message": "Déconnexion réussie",
            "redirect_url": "/accounts/login/",
        }
    )


@require_http_methods(["GET"])
def check_email_availability(request):
    """Verificar disponibilidade de email via AJAX"""

    email = request.GET.get("email", "").strip().lower()

    if not email:
        return JsonResponse({"available": False, "message": "Email requis"})

    if User.objects.filter(email=email).exists():
        return JsonResponse({"available": False, "message": "Email déjà utilisé"})

    return JsonResponse({"available": True, "message": "Email disponible"})


# ==================== UTILITY VIEWS ====================
def get_client_ip(request):
    """Obter IP do cliente"""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip
