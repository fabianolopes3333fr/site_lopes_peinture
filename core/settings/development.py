"""
Configurações específicas para desenvolvimento
"""
from .base import *
from decouple import config

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]


# Configurações do CORS
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ✅ Configurações específicas para testes
if 'test' in sys.argv:
    # Usar base de dados em memória para testes
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
    
    # Desabilitar migrações para acelerar testes
    class DisableMigrations:
        def __contains__(self, item):
            return True
        def __getitem__(self, item):
            return None
    
    MIGRATION_MODULES = DisableMigrations()
    
    # Usar diretório temporário para media nos testes
    import tempfile
    MEDIA_ROOT = tempfile.mkdtemp()
# Email
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Debug toolbar
INSTALLED_APPS += [
    # "debug_toolbar",
    "django_extensions",
    "django_browser_reload",
]

MIDDLEWARE = [
    "django_browser_reload.middleware.BrowserReloadMiddleware",
    # "debug_toolbar.middleware.DebugToolbarMiddleware",
] + MIDDLEWARE

INTERNAL_IPS = ["127.0.0.1"]

# Criar diretório de logs
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)