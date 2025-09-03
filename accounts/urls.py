from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name = "accounts"

urlpatterns = [
    # Autenticação
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("ajax/logout/", views.ajax_logout, name="ajax_logout"),
    
    # Reset de senha
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="accounts/password_reset.html",
            email_template_name="accounts/emails/password_reset_email.html",
            subject_template_name="accounts/emails/password_reset_subject.txt",
            success_url="/accounts/password-reset/done/",
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
            template_name="accounts/password_reset_confirm.html",
            success_url="/accounts/password-reset/complete/",
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
    
    # Perfil e Dashboard
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("settings/", views.account_settings, name="settings"),
    
    # Gerenciamento de senha e conta
    path("change-password/", views.change_password, name="change_password"),
    path("delete-account/", views.delete_account, name="delete_account"),
    path("update-email/", views.update_email, name="update_email"),
    
    # AJAX endpoints
    path("ajax/user-data/", views.get_user_data, name="get_user_data"),
    path("ajax/upload-avatar/", views.upload_avatar, name="upload_avatar"),
    path("ajax/remove-avatar/", views.remove_avatar, name="remove_avatar"),
    path("ajax/check-email/", views.check_email_exists, name="check_email_exists"),
    
    # Verificação de email
    path("verify-email/<str:token>/", views.verify_email, name="verify_email"),
    path("resend-verification/", views.resend_verification_email, name="resend_verification"),
    
    # Exportação de dados (GDPR)
    path("export-data/", views.export_user_data, name="export_user_data"),
    
    # Segurança
    path("security-log/", views.security_log, name="security_log"),
    
    # Administração (apenas superadmin)
    path("admin/", views.admin_dashboard, name="admin_dashboard"),
    path("admin/users/", views.admin_users_list, name="admin_users_list"),
    path(
        "admin/users/<int:user_id>/toggle-status/",
        views.admin_toggle_user_status,
        name="admin_toggle_user_status",
    ),
    
    # API endpoints
    path("api/profile/", views.api_user_profile, name="api_user_profile"),
    path("api/stats/", views.api_users_stats, name="api_users_stats"),
    
    # Views de erro
    path("account-locked/", views.account_locked_view, name="account_locked"),
    path("email-not-verified/", views.email_not_verified_view, name="email_not_verified"),
    
    # Views de compatibilidade (para URLs antigas)
    path("register-old/", views.register_view, name="register_old"),
    path("profile-old/", views.profile_view, name="profile_old"),
    path("dashboard-old/", views.dashboard_view, name="dashboard_old"),
    
    # Incluir URLs do django-allauth se estiver sendo usado
    path("social/", include("allauth.urls")),
   
]