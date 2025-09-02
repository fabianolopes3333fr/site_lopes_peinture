from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name = "accounts"

urlpatterns = [
    # Autenticação
    path("register/", views.register_view, name="register"),
    path("login/", views.user_login_view, name="login"),
    path("logout/", views.user_logout_view, name="logout"),
    path("ajax/logout/", views.ajax_logout_view, name="ajax_logout"),
    # Reset de senha
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="accounts/password_reset.html",
            email_template_name="accounts/password_reset_email.html",
            subject_template_name="accounts/password_reset_subject.txt",
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "password-reset/confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("change-password/", views.change_password, name="change_password"),
    # AJAX endpoints
    path("ajax/user-data/", views.get_user_data, name="get_user_data"),
    path("ajax/check-email/", views.check_email_exists, name="check_email_exists"),
    # Administração (apenas superadmin)
    path("admin/users/", views.admin_users_list, name="admin_users_list"),
    path(
        "admin/users/<int:user_id>/toggle-status/",
        views.admin_toggle_user_status,
        name="admin_toggle_user_status",
    ),
    # Verificação de email
    path("verify-email/<str:token>/", views.verify_email, name="verify_email"),
    # Incluir URLs do django-allauth se estiver sendo usado
    path("social/", include("allauth.urls")),
]
