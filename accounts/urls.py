from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    # ==================== AUTENTICAÇÃO ====================
    # Registro
    path("register/", views.RegisterView.as_view(), name="register"),

    # Login
    path("login/", views.user_login, name="login"),
    
    # Logout (suporta GET e POST)
    path("logout/", views.user_logout, name="logout"),
    
    # ==================== RESET SENHA ==================
    # Fluxo de reset de senha
    path("password_reset/", views.password_reset_view, name="password_reset"),
    path("password_reset/done/", views.password_reset_done_view, name="password_reset_done"),
    path("password_reset/<uidb64>/<token>/", views.password_reset_confirm_view, name="password_reset_confirm"),
    # ==================== DASHBOARD ====================
    # Dashboard principal
    path("dashboard/", views.dashboard, name="dashboard"),
    
    # Perfil básico (redirecionará para profiles app)
    path("profile/", views.profile, name="profile"),
    
    # ==================== AJAX ENDPOINTS ====================
    # Logout via AJAX
    path("ajax/logout/", views.ajax_logout, name="ajax_logout"),
    
    # Verificação de disponibilidade de email
    path("ajax/check-email/", views.check_email_availability, name="check_email"),
    
    # ==================== REDIRECTS ÚTEIS ====================
    # Redirect para dashboard (URL amigável)
    path("", views.dashboard, name="index"),
]