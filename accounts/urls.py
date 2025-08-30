from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name = "accounts"

urlpatterns = [
    # Autenticação
    path('register/', views.register_view, name='register'),
    path('login/', views.user_login_view, name='login'),
    path('logout/', views.user_logout_view, name='logout'),
    path('ajax/logout/', views.ajax_logout_view, name='ajax_logout'),
    # Reset de senha
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='accounts/password_reset.html',
             email_template_name='accounts/password_reset_email.html',
             subject_template_name='accounts/password_reset_subject.txt'
         ),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('password-reset/confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),
    path('password-reset/complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html'
         ),
         name='password_reset_complete'),
    # Perfil
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('change-password/', views.change_password, name='change_password'),
    path('delete-account/', views.delete_account, name='delete_account'),
    # Projetos
    path('mes-projets/', views.mes_projets, name='mes_projets'),
    path('criar-projeto/', views.criar_projeto, name='criar_projeto'),
    path('projeto/<int:projeto_id>/', views.projeto_detail, name='projeto_detail'),
    path('projeto/<int:projeto_id>/editar/', views.editar_projeto, name='editar_projeto'),
    path('projeto/<int:projeto_id>/deletar/', views.deletar_projeto, name='deletar_projeto'),
    
    # AJAX endpoints
    path('ajax/user-data/', views.get_user_data, name='get_user_data'),
    path('ajax/upload-avatar/', views.upload_avatar, name='upload_avatar'),
    path('ajax/remove-avatar/', views.remove_avatar, name='remove_avatar'),
    path('ajax/check-email/', views.check_email_exists, name='check_email_exists'),
    
    # Exportação de dados
    path('export-data/', views.export_user_data, name='export_user_data'),
    
    # Administração (apenas superadmin)
    path('admin/users/', views.admin_users_list, name='admin_users_list'),
    path('admin/users/<int:user_id>/toggle-status/', views.admin_toggle_user_status, name='admin_toggle_user_status'),
    
    # Verificação de email
    path('verify-email/<str:token>/', views.verify_email, name='verify_email'),
    
    # Incluir URLs do django-allauth se estiver sendo usado
    path('social/', include('allauth.urls')),
]
