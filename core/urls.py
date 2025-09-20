"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

from core import views


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
    path("", include("accounts.urls")),
    # Profiles (perfis de usuário)
    path("", include("profiles.urls")),
    # Config (configurações do site)
    path("", include("config.urls")),
    # Projects (projetos/serviços)
    path("", include("projects.urls")),
    # Pages (páginas principais)
    path("", include("pages.urls")),
    # ==================== REDIRECTS ÚTEIS ====================
    # Redirect para área do usuário logado
    path("dashboard/", redirect_to_accounts),
    path("accounts/", redirect_to_accounts),
    path("mon-compte/", redirect_to_accounts),
    path("test-tailwind/", views.test_tailwind, name="test_tailwind"),
]

# Adicionar URLs do django_browser_reload apenas em desenvolvimento
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
