from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect


def redirect_to_accounts(request):
    """Redirect raiz para accounts se autenticado, senão para home"""
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")
    return redirect("pages:home")


urlpatterns = [
    # ==================== ADMIN ====================
    path("admin/", admin.site.urls),
    # ==================== APPS ====================
    # Accounts (autenticação)
    path("accounts/", include("accounts.urls")),
    # Profiles (perfis de usuário)
    path("profiles/", include("profiles.urls")),
    # Config (configurações do site)
    path("config/", include("config.urls")),
    # Projects (projetos/serviços)
    path("projects/", include("projects.urls")),
    # Pages (páginas principais)
    path("", include("pages.urls")),
    # ==================== REDIRECTS ÚTEIS ====================
    # Redirect para área do usuário logado
    path("dashboard/", redirect_to_accounts),
    path("my-account/", redirect_to_accounts),
    path("mon-compte/", redirect_to_accounts),
]

# ==================== DESENVOLVIMENTO ====================
if settings.DEBUG:
    # URLs do django_browser_reload (se estiver habilitado)
    try:
        urlpatterns = [
            path("__reload__/", include("django_browser_reload.urls")),
        ] + urlpatterns
    except:
        pass  # Ignore se django_browser_reload não estiver instalado

    # Servir arquivos de mídia durante desenvolvimento
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# ==================== HANDLER DE ERROS (Opcional) ====================
# Você pode adicionar depois se quiser páginas de erro personalizadas
# handler404 = 'pages.views.error_404'
# handler500 = 'pages.views.error_500'
