import csv
import uuid
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta


def generate_verification_token(user):
    """
    Gera um token único para verificação de email
    """
    token = uuid.uuid4()
    user.verification_token = token
    user.save(update_fields=["verification_token"])
    return token


def export_user_data_to_csv(user):
    """
    Exporta os dados do usuário e seus projetos para CSV
    """
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
        f'attachment; filename="user_data_{user.id}_{timezone.now().date()}.csv"'
    )

    writer = csv.writer(response)

    # Informações do usuário
    writer.writerow(["INFORMATIONS UTILISATEUR"])
    writer.writerow(["Email", "Nom", "Prénom", "Date d'inscription"])
    writer.writerow(
        [
            user.email,
            user.last_name,
            user.first_name,
            user.date_joined.strftime("%d/%m/%Y"),
        ]
    )

    # Informações do perfil
    writer.writerow([])
    writer.writerow(["PROFIL"])
    writer.writerow(["Téléphone", "Adresse", "Date de naissance"])
    writer.writerow(
        [
            user.profile.phone if hasattr(user, "profile") else "",
            user.profile.address if hasattr(user, "profile") else "",
            (
                user.profile.date_of_birth.strftime("%d/%m/%Y")
                if hasattr(user, "profile") and user.profile.date_of_birth
                else ""
            ),
        ]
    )

    # Projetos do usuário
    writer.writerow([])
    writer.writerow(["PROJETS"])
    writer.writerow(
        [
            "Type",
            "Description",
            "Surface (m²)",
            "Date début",
            "Date fin",
            "Urgence",
            "Adresse",
            "Ville",
            "Status",
            "Date création",
        ]
    )

    for project in user.projects.all():
        writer.writerow(
            [
                project.get_type_projet_display(),
                project.description,
                project.surface,
                (
                    project.date_debut_souhaitee.strftime("%d/%m/%Y")
                    if project.date_debut_souhaitee
                    else ""
                ),
                (
                    project.date_fin_souhaitee.strftime("%d/%m/%Y")
                    if project.date_fin_souhaitee
                    else ""
                ),
                project.get_urgence_display(),
                project.adresse_travaux,
                project.ville,
                project.get_status_display(),
                project.created_at.strftime("%d/%m/%Y"),
            ]
        )

    return response


def is_token_expired(token_date, expire_days=1):
    """
    Verifica se um token expirou
    """
    if not token_date:
        return True
    return token_date + timedelta(days=expire_days) < timezone.now()


def get_client_ip(request):
    """
    Obtém o IP do cliente
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip
