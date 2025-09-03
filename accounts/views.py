import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView,
)
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import cache_control, never_cache
from django.http import JsonResponse, HttpResponseForbidden, Http404
from django.urls import reverse, reverse_lazy
from django.core.mail import send_mail
from django.conf import settings
from django.utils.decorators import method_decorator
from django.db.models import Q, Count
from django.core.exceptions import PermissionDenied, ValidationError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.serializers import serialize
from django.utils.timezone import localtime, now
from django.core.validators import validate_email
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from .models import User
from .forms import (
    UserRegistrationForm,
    PasswordChangeForm,
    UserLoginForm,
    PasswordResetForm,
    UserProfileForm,
)
from .decorators import superuser_required, permission_required
from .utils import generate_verification_token, export_user_data_to_csv

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """Obtém o IP do cliente."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


# ==================== VIEWS DE AUTENTICAÇÃO ====================


@method_decorator([csrf_protect, never_cache], name="dispatch")
class RegisterView(CreateView):
    """
    View para registro de novos usuários com verificação por email.
    """

    model = User
    form_class = UserRegistrationForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("accounts:login")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("accounts:dashboard")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """
        Processa o registro do usuário e envia email de verificação.
        """
        try:
            with transaction.atomic():
                user = form.save(commit=False)
                user.is_active = False  # Aguarda verificação por email
                user.save()

                # Log do registro
                logger.info(
                    f"Novo usuário registrado: {user.email} - IP: {get_client_ip(self.request)}"
                )

                # Envia email de verificação
                self.send_verification_email(user)

                messages.success(
                    self.request,
                    _(
                        "Compte créé avec succès! Veuillez vérifier votre email pour activer votre compte."
                    ),
                )

                return redirect(self.success_url)

        except Exception as e:
            logger.error(
                f"Erro no registro do usuário {form.cleaned_data.get('email')}: {str(e)}"
            )
            messages.error(
                self.request,
                _(
                    "Une erreur s'est produite lors de la création du compte. Veuillez réessayer."
                ),
            )
            return self.form_invalid(form)

    def send_verification_email(self, user):
        """
        Envia email de verificação para o usuário.
        """
        try:
            token = generate_verification_token(user)
            verification_url = self.request.build_absolute_uri(
                reverse("accounts:verify_email", kwargs={"token": token})
            )

            # Renderizar template HTML
            html_message = render_to_string(
                "accounts/emails/verification_email.html",
                {
                    "user": user,
                    "verification_url": verification_url,
                    "site_name": "Lopes Peinture",
                },
            )
            plain_message = strip_tags(html_message)

            send_mail(
                subject=_("Vérifiez votre adresse email - Lopes Peinture"),
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )

            logger.info(f"Email de verificação enviado para: {user.email}")

        except Exception as e:
            logger.error(
                f"Erro ao enviar email de verificação para {user.email}: {str(e)}"
            )
            raise


register = RegisterView.as_view()


@csrf_protect
@never_cache
@require_http_methods(["GET", "POST"])
def user_login(request):
    """
    View de login com proteção contra ataques de força bruta.
    """
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")

    if request.method == "POST":
        form = UserLoginForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()

            # Verificar se o usuário não está bloqueado (se implementado no modelo)
            if hasattr(user, "is_locked_out") and user.is_locked_out():
                messages.error(
                    request,
                    _(
                        "Votre compte est temporairement verrouillé en raison de trop nombreuses tentatives de connexion échouées."
                    ),
                )
                return render(request, "accounts/login.html", {"form": form})

            # Login bem-sucedido
            login(request, user)

            # Log do login
            logger.info(
                f"Login bem-sucedido: {user.email} - IP: {get_client_ip(request)}"
            )

            # Reset tentativas falhadas (se implementado)
            if hasattr(user, "reset_failed_login"):
                user.reset_failed_login()

            # Redirecionamento
            next_url = request.GET.get("next")
            if next_url and next_url.startswith("/"):
                return redirect(next_url)

            return redirect("accounts:dashboard")

        else:
            # Log da tentativa de login falhada
            email = request.POST.get("username", "")
            logger.warning(
                f"Tentativa de login falhada para: {email} - IP: {get_client_ip(request)}"
            )

            messages.error(request, _("Email ou mot de passe invalide."))

    else:
        form = UserLoginForm()

    return render(request, "accounts/login.html", {"form": form})


@login_required
@require_POST
def user_logout(request):
    """
    View de logout com log de segurança.
    """
    user_email = request.user.email
    logger.info(f"Logout: {user_email} - IP: {get_client_ip(request)}")

    logout(request)
    messages.success(request, _("Vous avez été déconnecté avec succès."))

    return redirect("home:home")


@login_required
@require_POST
def ajax_logout(request):
    """
    Logout via AJAX.
    """
    user_email = request.user.email
    logger.info(f"Logout AJAX: {user_email} - IP: {get_client_ip(request)}")

    logout(request)
    return JsonResponse({"status": "success", "message": _("Déconnexion réussie")})


# ==================== VERIFICAÇÃO DE EMAIL ====================


@never_cache
def verify_email(request, token):
    """
    Verifica o email do usuário através do token.
    """
    try:
        user = User.objects.get(verification_token=token)

        if user.is_active:
            messages.info(request, _("Votre email est déjà vérifié."))
            return redirect("accounts:login")

        # Ativar usuário
        user.is_active = True
        if hasattr(user, "email_verified"):
            user.email_verified = True
        user.verification_token = ""
        user.save()

        logger.info(f"Email verificado com sucesso: {user.email}")

        messages.success(
            request,
            _("Email vérifié avec succès! Vous pouvez maintenant vous connecter."),
        )

        return redirect("accounts:login")

    except User.DoesNotExist:
        logger.warning(f"Token de verificação inválido: {token}")
        messages.error(request, _("Lien de vérification invalide ou expiré."))
        return redirect("accounts:register")


# ==================== DASHBOARD E PERFIL ====================


@method_decorator(login_required, name="dispatch")
class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Dashboard básico do usuário - pode ser estendido por outras apps.
    """

    template_name = "accounts/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context.update(
            {
                "user": user,
                "account_created": user.date_joined,
                "last_login": user.last_login,
                "user_projects": self.request.user.client_projects.select_related(
                    "category"
                ).all(),
            }
        )

        return context


dashboard = DashboardView.as_view()


@method_decorator([login_required, never_cache], name="dispatch")
class ProfileView(UpdateView):
    """
    View para visualização e edição do perfil do usuário.
    """

    model = User
    form_class = UserProfileForm
    template_name = "accounts/profile.html"
    success_url = reverse_lazy("accounts:profile")

    @method_decorator(cache_control(private=True, no_cache=True))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, _("Profil mis à jour avec succès!"))
        logger.info(f"Perfil atualizado: {self.request.user.email}")
        return super().form_valid(form)


profile = ProfileView.as_view()


@login_required
def change_password(request):
    """
    View para alteração de senha.
    """
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)

        if form.is_valid():
            user = form.save()

            # Atualiza a sessão para manter o usuário logado
            update_session_auth_hash(request, user)

            # Log da alteração de senha
            logger.info(f"Senha alterada: {user.email} - IP: {get_client_ip(request)}")

            messages.success(request, _("Votre mot de passe a été changé avec succès!"))
            return redirect("accounts:profile")
        else:
            messages.error(request, _("Veuillez corriger les erreurs ci-dessous."))
    else:
        form = PasswordChangeForm(request.user)

    return render(request, "accounts/change_password.html", {"form": form})


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

                # Enviar email
                html_message = render_to_string(
                    "accounts/emails/password_reset_email.html",
                    {
                        "user": user,
                        "reset_url": reset_url,
                        "site_name": "Lopes Peinture",
                    },
                )
                plain_message = strip_tags(html_message)

                send_mail(
                    subject=_("Réinitialisation de mot de passe - Lopes Peinture"),
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    html_message=html_message,
                    fail_silently=False,
                )

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


def password_reset_done_view(request):
    """
    View de confirmação de envio do email de reset.
    """
    return render(request, "accounts/password_reset_done.html")


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
            form = PasswordResetForm(request.POST)

            if form.is_valid():
                new_password = form.cleaned_data["new_password1"]
                user.set_password(new_password)
                user.save()

                logger.info(f"Senha resetada com sucesso para: {user.email}")

                messages.success(
                    request, _("Votre mot de passe a été réinitialisé avec succès!")
                )
                return redirect("accounts:password_reset_complete")
        else:
            form = PasswordResetForm()

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


def password_reset_complete_view(request):
    """
    View de confirmação de reset completo.
    """
    return render(request, "accounts/password_reset_complete.html")


# ==================== GERENCIAMENTO DE CONTA ====================


@login_required
@require_POST
def delete_account(request):
    """
    View para exclusão de conta do usuário.
    """
    user = request.user

    # Verificar senha antes de deletar
    password = request.POST.get("password")
    if not user.check_password(password):
        messages.error(request, _("Mot de passe incorrect."))
        return redirect("accounts:profile")

    # Log da exclusão
    logger.info(f"Conta deletada: {user.email} - IP: {get_client_ip(request)}")

    # Logout e deletar
    logout(request)
    user.delete()

    messages.success(request, _("Votre compte a été supprimé avec succès."))
    return redirect("home:home")


@login_required
def export_user_data(request):
    """
    Exporta os dados do usuário em formato CSV (GDPR compliance).
    """
    user = request.user

    try:
        response = export_user_data_to_csv(user)
        logger.info(f"Dados exportados para: {user.email}")
        return response
    except Exception as e:
        logger.error(f"Erro na exportação de dados para {user.email}: {str(e)}")
        messages.error(request, _("Erreur lors de l'exportation des données."))
        return redirect("accounts:profile")


# ==================== VIEWS AJAX ====================


@login_required
@require_POST
def upload_avatar(request):
    """
    Upload de avatar via AJAX.
    """
    if "avatar" not in request.FILES:
        return JsonResponse({"error": _("Aucun fichier sélectionné")}, status=400)

    avatar_file = request.FILES["avatar"]

    # Validações básicas
    if avatar_file.size > 5 * 1024 * 1024:  # 5MB
        return JsonResponse(
            {"error": _("Fichier trop volumineux (max 5MB)")}, status=400
        )

    if not avatar_file.content_type.startswith("image/"):
        return JsonResponse({"error": _("Format de fichier invalide")}, status=400)

    try:
        user = request.user
        user.avatar = avatar_file
        user.save()

        logger.info(f"Avatar atualizado para: {user.email}")

        return JsonResponse(
            {
                "success": True,
                "avatar_url": user.avatar.url if user.avatar else None,
                "message": _("Avatar mis à jour avec succès!"),
            }
        )
    except Exception as e:
        logger.error(f"Erro no upload de avatar para {request.user.email}: {str(e)}")
        return JsonResponse({"error": _("Erreur lors du téléchargement")}, status=500)


@login_required
@require_POST
def remove_avatar(request):
    """
    Remove o avatar do usuário via AJAX.
    """
    try:
        user = request.user
        if user.avatar:
            user.avatar.delete()
            user.save()

        logger.info(f"Avatar removido para: {user.email}")

        return JsonResponse(
            {"success": True, "message": _("Avatar supprimé avec succès!")}
        )
    except Exception as e:
        logger.error(f"Erro na remoção de avatar para {request.user.email}: {str(e)}")
        return JsonResponse({"error": _("Erreur lors de la suppression")}, status=500)


@login_required
def get_user_data(request):
    """
    Retorna dados do usuário em formato JSON.
    """
    user = request.user

    data = {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "date_joined": user.date_joined.isoformat() if user.date_joined else None,
        "last_login": user.last_login.isoformat() if user.last_login else None,
        "avatar_url": user.avatar.url if user.avatar else None,
    }

    return JsonResponse(data)


@require_POST
def check_email_exists(request):
    """
    Verifica se um email já existe no sistema (para validação em tempo real).
    """
    email = request.POST.get("email", "").lower().strip()

    if not email:
        return JsonResponse({"error": _("Email requis")}, status=400)

    try:
        validate_email(email)
    except ValidationError:
        return JsonResponse({"error": _("Format d'email invalide")}, status=400)

    exists = User.objects.filter(email=email).exists()

    return JsonResponse(
        {
            "exists": exists,
            "message": (
                _("Cet email est déjà utilisé") if exists else _("Email disponible")
            ),
        }
    )


# ==================== VIEWS DE ADMINISTRAÇÃO ====================


@superuser_required
def admin_users_list(request):
    """
    Lista de usuários para administradores.
    """
    search_query = request.GET.get("search", "")
    status_filter = request.GET.get("status", "")

    users = User.objects.all().order_by("-date_joined")

    # Filtros
    if search_query:
        users = users.filter(
            Q(email__icontains=search_query)
            | Q(first_name__icontains=search_query)
            | Q(last_name__icontains=search_query)
        )

    if status_filter == "active":
        users = users.filter(is_active=True)
    elif status_filter == "inactive":
        users = users.filter(is_active=False)

    # Paginação
    paginator = Paginator(users, 25)
    page = request.GET.get("page")

    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)

    context = {
        "users": users,
        "search_query": search_query,
        "status_filter": status_filter,
        "total_users": User.objects.count(),
        "active_users": User.objects.filter(is_active=True).count(),
        "inactive_users": User.objects.filter(is_active=False).count(),
    }

    return render(request, "accounts/admin/users_list.html", context)


@superuser_required
@require_POST
def admin_toggle_user_status(request, user_id):
    """
    Ativa/desativa um usuário (apenas para superusuários).
    """
    try:
        user = get_object_or_404(User, id=user_id)

        # Não permitir desativar o próprio usuário
        if user == request.user:
            return JsonResponse(
                {"error": _("Vous ne pouvez pas désactiver votre propre compte")},
                status=400,
            )

        user.is_active = not user.is_active
        user.save()

        action = "ativado" if user.is_active else "desativado"
        logger.info(
            f"Usuário {action} por admin: {user.email} - Admin: {request.user.email}"
        )

        return JsonResponse(
            {
                "success": True,
                "is_active": user.is_active,
                "message": _("Statut de l'utilisateur mis à jour avec succès!"),
            }
        )

    except Exception as e:
        logger.error(f"Erro ao alterar status do usuário {user_id}: {str(e)}")
        return JsonResponse({"error": _("Erreur lors de la mise à jour")}, status=500)


# ==================== VIEWS AUXILIARES ====================


def is_superuser(user):
    """
    Verifica se o usuário é superusuário.
    """
    return user.is_authenticated and user.is_superuser


@user_passes_test(is_superuser)
def admin_dashboard(request):
    """
    Dashboard administrativo com estatísticas básicas.
    """
    context = {
        "total_users": User.objects.count(),
        "active_users": User.objects.filter(is_active=True).count(),
        "inactive_users": User.objects.filter(is_active=False).count(),
        "recent_users": User.objects.filter(is_active=True).order_by("-date_joined")[
            :10
        ],
        "staff_users": User.objects.filter(is_staff=True).count(),
    }

    return render(request, "accounts/admin/dashboard.html", context)


# ==================== VIEWS DE FUNÇÃO (COMPATIBILIDADE) ====================


def register_view(request):
    """
    View de função para registro (compatibilidade com URLs antigas).
    """
    return RegisterView.as_view()(request)


def profile_view(request):
    """
    View de função para perfil (compatibilidade com URLs antigas).
    """
    return ProfileView.as_view()(request)


def dashboard_view(request):
    """
    View de função para dashboard (compatibilidade com URLs antigas).
    """
    return DashboardView.as_view()(request)


# ==================== VIEWS DE ERRO PERSONALIZADAS ====================


def account_locked_view(request):
    """
    View para conta bloqueada.
    """
    return render(request, "accounts/account_locked.html", status=423)


def email_not_verified_view(request):
    """
    View para email não verificado.
    """
    return render(request, "accounts/email_not_verified.html")


# ==================== VIEWS DE NOTIFICAÇÕES ====================


@login_required
def resend_verification_email(request):
    """
    Reenvia email de verificação.
    """
    user = request.user

    if user.is_active and hasattr(user, "email_verified") and user.email_verified:
        messages.info(request, _("Votre email est déjà vérifié."))
        return redirect("accounts:dashboard")

    try:
        # Gerar novo token
        token = generate_verification_token(user)
        user.verification_token = token
        user.save()

        # Enviar email
        verification_url = request.build_absolute_uri(
            reverse("accounts:verify_email", kwargs={"token": token})
        )

        html_message = render_to_string(
            "accounts/emails/verification_email.html",
            {
                "user": user,
                "verification_url": verification_url,
                "site_name": "Lopes Peinture",
            },
        )
        plain_message = strip_tags(html_message)

        send_mail(
            subject=_("Vérifiez votre adresse email - Lopes Peinture"),
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(f"Email de verificação reenviado para: {user.email}")
        messages.success(request, _("Email de vérification renvoyé avec succès!"))

    except Exception as e:
        logger.error(
            f"Erro ao reenviar email de verificação para {user.email}: {str(e)}"
        )
        messages.error(request, _("Erreur lors de l'envoi de l'email."))

    return redirect("accounts:dashboard")


# ==================== VIEWS DE CONFIGURAÇÕES ====================


@login_required
def account_settings(request):
    """
    View para configurações da conta.
    """
    user = request.user

    context = {
        "user": user,
        "can_delete_account": True,  # Pode ser baseado em regras de negócio
        "email_verified": getattr(user, "email_verified", True),
        "two_factor_enabled": getattr(user, "two_factor_enabled", False),
    }

    return render(request, "accounts/settings.html", context)


@login_required
@require_POST
def update_email(request):
    """
    Atualiza o email do usuário com verificação.
    """
    new_email = request.POST.get("email", "").lower().strip()

    if not new_email:
        messages.error(request, _("Email requis."))
        return redirect("accounts:settings")

    try:
        validate_email(new_email)
    except ValidationError:
        messages.error(request, _("Format d'email invalide."))
        return redirect("accounts:settings")

    # Verificar se o email já existe
    if User.objects.filter(email=new_email).exclude(id=request.user.id).exists():
        messages.error(request, _("Cet email est déjà utilisé."))
        return redirect("accounts:settings")

    # Verificar senha atual
    current_password = request.POST.get("current_password")
    if not request.user.check_password(current_password):
        messages.error(request, _("Mot de passe actuel incorrect."))
        return redirect("accounts:settings")

    try:
        user = request.user
        old_email = user.email
        user.email = new_email

        # Marcar email como não verificado se implementado
        if hasattr(user, "email_verified"):
            user.email_verified = False

        user.save()

        logger.info(f"Email alterado de {old_email} para {new_email}")

        # Enviar email de verificação para o novo email
        if hasattr(user, "email_verified"):
            token = generate_verification_token(user)
            user.verification_token = token
            user.save()

            verification_url = request.build_absolute_uri(
                reverse("accounts:verify_email", kwargs={"token": token})
            )

            html_message = render_to_string(
                "accounts/emails/email_change_verification.html",
                {
                    "user": user,
                    "verification_url": verification_url,
                    "old_email": old_email,
                    "new_email": new_email,
                    "site_name": "Lopes Peinture",
                },
            )
            plain_message = strip_tags(html_message)

            send_mail(
                subject=_("Vérifiez votre nouvelle adresse email - Lopes Peinture"),
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[new_email],
                html_message=html_message,
                fail_silently=False,
            )

        messages.success(
            request,
            _(
                "Email mis à jour avec succès! Veuillez vérifier votre nouvelle adresse."
            ),
        )

    except Exception as e:
        logger.error(f"Erro ao alterar email para {request.user.email}: {str(e)}")
        messages.error(request, _("Erreur lors de la mise à jour de l'email."))

    return redirect("accounts:settings")


# ==================== VIEWS DE SEGURANÇA ====================


@login_required
def security_log(request):
    """
    Exibe log de atividades de segurança do usuário.
    """
    # Esta view pode ser expandida para mostrar logs de login, alterações, etc.
    # Por enquanto, mostra informações básicas

    user = request.user

    context = {
        "user": user,
        "last_login": user.last_login,
        "date_joined": user.date_joined,
        "password_changed": getattr(user, "password_changed_at", None),
        "login_attempts": getattr(user, "failed_login_attempts", 0),
    }

    return render(request, "accounts/security_log.html", context)


# ==================== VIEWS DE API (JSON) ====================


@login_required
def api_user_profile(request):
    """
    API endpoint para dados do perfil do usuário.
    """
    user = request.user

    data = {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "full_name": user.get_full_name(),
        "date_joined": user.date_joined.isoformat() if user.date_joined else None,
        "last_login": user.last_login.isoformat() if user.last_login else None,
        "is_active": user.is_active,
        "is_staff": user.is_staff,
        "avatar_url": (
            user.avatar.url if hasattr(user, "avatar") and user.avatar else None
        ),
        "email_verified": getattr(user, "email_verified", True),
    }

    return JsonResponse(data)


@superuser_required
def api_users_stats(request):
    """
    API endpoint para estatísticas de usuários (apenas superusuários).
    """
    from django.db.models import Count
    from django.utils import timezone
    from datetime import timedelta

    now = timezone.now()
    last_30_days = now - timedelta(days=30)

    stats = {
        "total_users": User.objects.count(),
        "active_users": User.objects.filter(is_active=True).count(),
        "inactive_users": User.objects.filter(is_active=False).count(),
        "staff_users": User.objects.filter(is_staff=True).count(),
        "superusers": User.objects.filter(is_superuser=True).count(),
        "new_users_last_30_days": User.objects.filter(
            date_joined__gte=last_30_days
        ).count(),
        "users_with_avatar": (
            User.objects.exclude(avatar="").count() if hasattr(User, "avatar") else 0
        ),
    }

    return JsonResponse(stats)


# ==================== HANDLERS DE ERRO ====================


def handle_user_not_found(request, exception=None):
    """
    Handler para usuário não encontrado.
    """
    messages.error(request, _("Utilisateur non trouvé."))
    return redirect("accounts:dashboard")


def handle_permission_denied(request, exception=None):
    """
    Handler para permissão negada.
    """
    messages.error(request, _("Vous n'avez pas la permission d'accéder à cette page."))
    return redirect("accounts:dashboard")


class ProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    View para atualização de perfil com verificação de permissão.
    """

    model = User
    form_class = UserProfileForm
    template_name = "accounts/profile_update.html"
    success_url = reverse_lazy("accounts:profile")

    def test_func(self):
        """
        Verifica se o usuário tem permissão para acessar esta view.
        """
        return self.request.user.is_authenticated

    def form_valid(self, form):
        messages.success(self.request, _("Profil mis à jour avec succès!"))
        logger.info(f"Profil mis à jour: {self.request.user.email}")
        return super().form_valid(form)

    def get_object(self):
        return self.request.user

    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
