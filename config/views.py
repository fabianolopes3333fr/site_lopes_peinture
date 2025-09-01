from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError
import json
import zipfile
import io
from datetime import datetime

import logging

# from .models import User, UserProfile, Project
logger = logging.getLogger(__name__)


# @login_require
def painel_view(request):
    return render(request, "dashboard/dashboard.html")


# @login_required
def settings_view(request):
    """View para exibir a página de configurações do usuário"""
    context = {
        "user": request.user,
        "page_title": "Paramètres",
    }
    return render(request, "dashboard/settings.html", context)


@login_required
@require_POST
def update_profile(request):
    """Atualizar informações do perfil do usuário"""
    try:
        user = request.user
        user.first_name = request.POST.get("first_name", "").strip()
        user.last_name = request.POST.get("last_name", "").strip()

        # Validar email se foi alterado
        new_email = request.POST.get("email", "").strip().lower()
        if new_email != user.email:
            # Verificar se o email já existe
            from django.contrib.auth import get_user_model

            User = get_user_model()
            if User.objects.filter(email=new_email).exclude(pk=user.pk).exists():
                messages.error(
                    request, "Cet email est déjà utilisé par un autre compte."
                )
                return redirect("config:settings")

            user.email = new_email

        user.save()
        messages.success(request, "Vos informations ont été mises à jour avec succès.")

    except Exception as e:
        messages.error(request, "Une erreur est survenue lors de la mise à jour.")

    return redirect("config:settings")


@login_required
@require_POST
def update_notifications(request):
    """Mettre à jour les préférences de notification"""
    try:
        profile = request.user.profile

        # Mettre à jour les préférences
        profile.email_notifications = "email_notifications" in request.POST
        profile.sms_notifications = "sms_notifications" in request.POST
        profile.newsletter = "newsletter" in request.POST
        profile.push_notifications = "push_notifications" in request.POST

        profile.save()
        messages.success(
            request, "Vos préférences de notification ont été sauvegardées."
        )

    except Exception as e:
        messages.error(request, "Erreur lors de la sauvegarde des préférences.")

    return redirect("config:settings")


@login_required
@require_POST
def change_password(request):
    """Changer le mot de passe de l'utilisateur"""
    form = PasswordChangeForm(request.user, request.POST)

    if form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        messages.success(request, "Votre mot de passe a été modifié avec succès.")
    else:
        for error in form.errors.values():
            messages.error(request, error[0])

    return redirect("config:settings")


@login_required
@require_POST
def export_data(request):
    """Exporter les données de l'utilisateur"""
    try:
        user = request.user

        # Créer un fichier ZIP en mémoire
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            # Données utilisateur
            user_data = {
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "date_joined": user.date_joined.isoformat(),
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "user_type": user.user_type,
                "is_verified": user.is_verified,
            }

            # Ajouter les données du profil si existe
            if hasattr(user, "profile"):
                profile_data = {
                    "phone": user.profile.phone,
                    "address": user.profile.address,
                    "city": user.profile.city,
                    "postal_code": user.profile.postal_code,
                    "email_notifications": user.profile.email_notifications,
                    "sms_notifications": user.profile.sms_notifications,
                    "newsletter": user.profile.newsletter,
                }
                user_data["profile"] = profile_data

            # Ajouter au ZIP
            zip_file.writestr(
                "user_data.json", json.dumps(user_data, indent=2, ensure_ascii=False)
            )

            # Ajouter d'autres données si nécessaire (projets, etc.)
            # ... code pour autres données

            # Fichier README
            readme_content = f"""
Exportation des données - Lopes Peinture
========================================

Date d'exportation: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
Utilisateur: {user.get_full_name()} ({user.email})

Contenu de l'archive:
- user_data.json: Informations personnelles et préférences
- README.txt: Ce fichier

Pour toute question, contactez-nous à contact@lopespeinture.fr
"""
            zip_file.writestr("README.txt", readme_content)

        zip_buffer.seek(0)

        # Préparer la réponse
        response = HttpResponse(zip_buffer.getvalue(), content_type="application/zip")
        response["Content-Disposition"] = (
            f'attachment; filename="donnees_{user.email}_{datetime.now().strftime("%Y%m%d")}.zip"'
        )

        return response

    except Exception as e:
        return JsonResponse({"error": "Erreur lors de l'export"}, status=500)


@login_required
@require_POST
def delete_account(request):
    """Supprimer définitivement le compte utilisateur"""
    try:
        user = request.user
        email = user.email

        # Log de sécurité
        import logging

        logger = logging.getLogger("config")
        logger.warning(f"Suppression de compte demandée pour {email}")

        # Supprimer l'utilisateur (cascade supprimera le profil)
        user.delete()

        messages.success(request, "Votre compte a été supprimé définitivement.")
        return redirect("page:home")

    except Exception as e:
        messages.error(request, "Erreur lors de la suppression du compte.")
        return redirect("config:settings")


@login_required
def login_history(request):
    """Afficher l'historique des connexions"""
    # Cette view nécessiterait un modèle pour stocker l'historique des connexions
    # Pour l'instant, on retourne une page simple
    context = {
        "page_title": "Historique des connexions",
        "login_sessions": [
            {
                "ip_address": request.META.get("REMOTE_ADDR", "Inconnue"),
                "user_agent": request.META.get("HTTP_USER_AGENT", "Inconnu"),
                "login_time": request.user.last_login,
                "is_current": True,
            }
        ],
    }
    return render(request, "dashboard/login_history.html", context)
