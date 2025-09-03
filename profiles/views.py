from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_POST
from django.http import JsonResponse, HttpResponseForbidden
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import UpdateView, DetailView
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
import logging

from .models import UserProfile
from .forms import UserProfileForm, AvatarUploadForm

logger = logging.getLogger(__name__)


class ProfileView(LoginRequiredMixin, UpdateView):
    """View para visualização e edição do perfil do usuário."""

    model = UserProfile
    form_class = UserProfileForm
    template_name = "profiles/profile.html"
    success_url = reverse_lazy("profiles:profile")
    context_object_name = "profile"

    def get_object(self):
        """Retorna o perfil do usuário logado."""
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        if created:
            logger.info(f"Perfil criado para o usuário {self.request.user.email}")
        return profile

    def get_form_kwargs(self):
        """Adiciona o usuário aos argumentos do formulário."""
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        """Processa o formulário válido."""
        response = super().form_valid(form)
        messages.success(self.request, _("Votre profil a été mis à jour avec succès."))
        logger.info(f"Perfil atualizado para o usuário {self.request.user.email}")
        return response

    def form_invalid(self, form):
        """Processa o formulário inválido."""
        messages.error(
            self.request,
            _(
                "Erreur lors de la mise à jour du profil. Veuillez corriger les erreurs."
            ),
        )
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        """Adiciona contexto extra."""
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "user": self.request.user,
                "avatar_form": AvatarUploadForm(instance=self.get_object()),
                "page_title": _("Mon Profil"),
            }
        )
        return context


class PublicProfileView(DetailView):
    """View para visualização pública do perfil (se implementado futuramente)."""

    model = UserProfile
    template_name = "profiles/public_profile.html"
    context_object_name = "profile"
    slug_field = "user__username"
    slug_url_kwarg = "username"

    def get_queryset(self):
        """Retorna apenas perfis de usuários ativos."""
        return UserProfile.objects.select_related("user").filter(user__is_active=True)


# AJAX Views
@login_required
@require_POST
def upload_avatar(request):
    """Endpoint AJAX para upload de avatar."""
    try:
        profile = get_object_or_404(UserProfile, user=request.user)
        form = AvatarUploadForm(request.POST, request.FILES, instance=profile)

        if form.is_valid():
            # Remove avatar antigo se existir
            if profile.avatar:
                try:
                    profile.avatar.delete(save=False)
                except Exception as e:
                    logger.warning(f"Erro ao remover avatar antigo: {e}")

            form.save()

            logger.info(f"Avatar atualizado para o usuário {request.user.email}")

            return JsonResponse(
                {
                    "status": "success",
                    "message": _("Avatar mis à jour avec succès"),
                    "avatar_url": profile.get_avatar_url(),
                }
            )
        else:
            errors = []
            for field, field_errors in form.errors.items():
                for error in field_errors:
                    errors.append(str(error))

            return JsonResponse(
                {
                    "status": "error",
                    "message": _("Erreur lors du téléchargement"),
                    "errors": errors,
                },
                status=400,
            )

    except Exception as e:
        logger.error(f"Erro no upload de avatar para {request.user.email}: {e}")
        return JsonResponse(
            {
                "status": "error",
                "message": _("Une erreur inattendue s'est produite"),
            },
            status=500,
        )


@login_required
@require_POST
def remove_avatar(request):
    """Endpoint AJAX para remoção de avatar."""
    try:
        profile = get_object_or_404(UserProfile, user=request.user)

        if profile.avatar:
            try:
                profile.avatar.delete()
                logger.info(f"Avatar removido para o usuário {request.user.email}")

                return JsonResponse(
                    {
                        "status": "success",
                        "message": _("Avatar supprimé avec succès"),
                        "avatar_url": profile.get_avatar_url(),  # URL padrão
                    }
                )
            except Exception as e:
                logger.error(f"Erro ao remover avatar: {e}")
                return JsonResponse(
                    {
                        "status": "error",
                        "message": _("Erreur lors de la suppression de l'avatar"),
                    },
                    status=500,
                )
        else:
            return JsonResponse(
                {
                    "status": "info",
                    "message": _("Aucun avatar à supprimer"),
                }
            )

    except Exception as e:
        logger.error(f"Erro na remoção de avatar para {request.user.email}: {e}")
        return JsonResponse(
            {
                "status": "error",
                "message": _("Une erreur inattendue s'est produite"),
            },
            status=500,
        )


@login_required
def get_profile_data(request):
    """Endpoint AJAX para obter dados do perfil."""
    try:
        profile = get_object_or_404(UserProfile, user=request.user)

        data = {
            "user": {
                "email": request.user.email,
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
                "full_name": request.user.get_full_name(),
                "is_verified": request.user.is_verified,
                "date_joined": request.user.date_joined.isoformat(),
            },
            "profile": {
                "avatar_url": profile.get_avatar_url(),
                "phone": profile.phone,
                "address": profile.address,
                "bio": profile.bio,
                "date_of_birth": (
                    profile.date_of_birth.isoformat() if profile.date_of_birth else None
                ),
                "age": profile.age,
                "created_at": profile.created_at.isoformat(),
                "updated_at": profile.updated_at.isoformat(),
            },
        }

        return JsonResponse(
            {
                "status": "success",
                "data": data,
            }
        )

    except Exception as e:
        logger.error(f"Erro ao obter dados do perfil para {request.user.email}: {e}")
        return JsonResponse(
            {
                "status": "error",
                "message": _("Erreur lors de la récupération des données"),
            },
            status=500,
        )
