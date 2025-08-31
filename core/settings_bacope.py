"""
Django settings for core project.
"""

import os
from pathlib import Path
from decouple import config
from django.core.exceptions import ImproperlyConfigured

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Define o ambiente com valor padrão 'development'


# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Debug tools
    "tailwind",
    "whitenoise",
    "theme",
    "django_browser_reload",  
    # Third party apps
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.facebook",
    # Local apps
    "accounts",
    'pages.apps.PagesConfig',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",  # Must be first
    "django_browser_reload.middleware.BrowserReloadMiddleware",
    # "debug_toolbar.middleware.DebugToolbarMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",  # Add CSRF middleware
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",  # Add clickjacking protection
    "allauth.account.middleware.AccountMiddleware",
    "requestlogs.middleware.RequestLogsMiddleware",
]
TAILWIND_APP_NAME = "theme"
INTERNAL_IPS = [
    "127.0.0.1",
]
NPM_BIN_PATH = "C:\\Program Files\\nodejs\\npm.cmd"


ROOT_URLCONF = "core.urls"


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates"
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

# Configurar o modelo de usuário customizado
AUTH_USER_MODEL = "accounts.User"

# URLs de redirecionamento após login/logout
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/accounts/dashboard/"
LOGOUT_REDIRECT_URL = "/"

# # Authentication backends
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# Allauth settings
SITE_ID = 1
# Configurações específicas do allauth
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]

# # Social auth providers
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": config("GOOGLE_OAUTH2_CLIENT_ID"),
            "secret": config("GOOGLE_OAUTH2_CLIENT_SECRET"),
            "key": "",
        }
    },
    "facebook": {
        "APP": {
            "client_id": config("FACEBOOK_APP_ID"),
            "secret": config("FACEBOOK_APP_SECRET"),
        }
    },
}
# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Europe/Paris"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / "static",  # Certifique-se que está usando BASE_DIR
]

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Email settings (base)
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "mail.lopespeinture.fr"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL")

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
# Define o ambiente com valor padrão 'development'
DJANGO_ENV = config("DJANGO_ENV", default="development")
# aprarti daqui configuracoes de seguranca
# Carrega as configurações apropriadas baseado no ambiente
if DJANGO_ENV == "production":
    # SECURITY WARNING: keep the secret key used in production secret!
    SECRET_KEY = config("SECRET_KEY")

    # SECURITY WARNING: don't run with debug turned on in production!
    DEBUG = config("DEBUG", default=False, cast=bool)

    # Permitir hosts do arquivo .env
    ALLOWED_HOSTS = config(
        "ALLOWED_HOSTS", default="lopespeinture.fr,www.lopespeinture.fr"
    ).split(",")

    if not ALLOWED_HOSTS:
        raise ImproperlyConfigured("ALLOWED_HOSTS must not be empty in production.")

    # Database
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": config("DB_NAME"),
            "USER": config("DB_USER"),
            "PASSWORD": config("DB_PASSWORD"),
            "HOST": config("DB_HOST", default="localhost"),
            "PORT": config("DB_PORT", default="5432"),
        }
    }

    MAX_FAILED_LOGIN_ATTEMPTS = 5
    SIREN_LENGTH = 9
    VAT_NUMBER_LENGTH = 14
    APE_CODE_LENGTH = 5
    # Default country
    DEFAULT_COUNTRY = "France"

    # Enhanced security settings
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

    # CSRF and Session settings
    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_HTTPONLY = True
    CSRF_COOKIE_SAMESITE = "Strict"
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Strict"

    # Frame options
    X_FRAME_OPTIONS = "DENY"
    
    # Admin configuration
    ADMINS = [
        (
            config('SUPER_USER', default='Admin'),
            config('ADMIN_EMAIL', default='admin@lopespeinture.fr')
        ),
    ]
    MANAGERS = ADMINS

    # Proteção contra ataques de força bruta
    AXES_ENABLED = True
    AXES_FAILURE_LIMIT = 5
    AXES_LOCK_OUT_AT_FAILURE = True
    AXES_COOLOFF_TIME = 1  # horas

    # Static files storage
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

    # Email settings for production
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
    EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
    EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
    EMAIL_HOST_USER = config("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
    DEFAULT_FROM_EMAIL = config(
        "DEFAULT_FROM_EMAIL", default="contact@lopespeinture.fr"
    )
    SERVER_EMAIL = config("SERVER_EMAIL", default="server@lopespeinture.fr")

    # Configuração de administradores para notificações de erro
    ADMINS = [
        ("Admin", config("ADMIN_EMAIL", default="admin@lopespeinture.fr")),
    ]
    MANAGERS = ADMINS
    SEND_WELCOME_EMAIL = True

    # URL base do site para links nos emails
    SITE_URL = "http://lopespeinture.fr"

    # Criar diretório de logs se não existir
    LOGS_DIR = BASE_DIR / "logs"
    LOGS_DIR.mkdir(exist_ok=True)

    # Logging Configuration
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {
                "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
                "style": "{",
            },
            "simple": {
                "format": "[{asctime}] {levelname} {message}",
                "style": "{",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "filters": {
            "require_debug_true": {
                "()": "django.utils.log.RequireDebugTrue",
            },
            "require_debug_false": {
                "()": "django.utils.log.RequireDebugFalse",
            },
        },
        "handlers": {
            "console": {
                "level": "INFO",
                "filters": ["require_debug_true"],
                "class": "logging.StreamHandler",
                "formatter": "simple",
            },
            "file_debug": {
                "level": "DEBUG",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": BASE_DIR / "logs" / "debug.log",
                "maxBytes": 1024 * 1024 * 5,  # 5 MB
                "backupCount": 5,
                "formatter": "verbose",
            },
            "file_error": {
                "level": "ERROR",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": BASE_DIR / "logs" / "error.log",
                "maxBytes": 1024 * 1024 * 5,  # 5 MB
                "backupCount": 5,
                "formatter": "verbose",
            },
            "mail_admins": {
                "level": "ERROR",
                "filters": ["require_debug_false"],
                "class": "django.utils.log.AdminEmailHandler",
                "formatter": "verbose",
            },
            "security": {
                "level": "INFO",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": BASE_DIR / "logs" / "security.log",
                "maxBytes": 1024 * 1024 * 5,  # 5 MB
                "backupCount": 5,
                "formatter": "verbose",
            },
        },
        "loggers": {
            "django": {
                "handlers": ["console", "file_debug"],
                "level": "INFO",
                "propagate": True,
            },
            "django.request": {
                "handlers": ["file_error", "mail_admins"],
                "level": "ERROR",
                "propagate": False,
            },
            "django.security": {
                "handlers": ["security", "mail_admins"],
                "level": "INFO",
                "propagate": False,
            },
            "accounts": {  # Para sua app de contas
                "handlers": ["console", "file_debug", "file_error"],
                "level": "INFO",
                "propagate": True,
            },
        },
    }

    # Configurações de cache
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": config("REDIS_URL", default="redis://localhost:6379/0"),
        }
    }

    # Configuração de sessão
    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    SESSION_CACHE_ALIAS = "default"

    # Configurações de template para produção
    TEMPLATES[0]["OPTIONS"]["loaders"] = [
        (
            "django.template.loaders.cached.Loader",
            [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
        ),
    ]

else:
    # AVISO DE SEGURANÇA: mantenha a chave secreta em segurança!
    SECRET_KEY = config("SECRET_KEY", default="your-secret-key-here")

    # AVISO DE SEGURANÇA: não execute com debug ativado em produção!
    DEBUG = config("DEBUG", default=True, cast=bool)

    ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

    # Configuração do banco de dados
    if config("USE_POSTGRES", default=False, cast=bool):
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": config("DB_NAME"),
                "USER": config("DB_USER"),
                "PASSWORD": config("DB_PASSWORD"),
                "HOST": config("DB_HOST", default="localhost"),
                "PORT": config("DB_PORT", default="5432", cast=int),
            }
        }
    else:
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": BASE_DIR / "db.sqlite3",
            }
        }

    # Configurações de email para desenvolvimento
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

    if DEBUG:
        INSTALLED_APPS += [
            "debug_toolbar",  # Adiciona apenas aqui
            "django_extensions",
        ]
        MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
        INTERNAL_IPS = ["127.0.0.1"]

    # Arquivos estáticos (CSS, JavaScript, Imagens)
    STATIC_URL = "/static/"
    STATIC_ROOT = BASE_DIR / "staticfiles"
    STATICFILES_DIRS = [BASE_DIR / "static"]

    # Arquivos de mídia (uploads de usuários)
    MEDIA_URL = "/media/"
    MEDIA_ROOT = BASE_DIR / "media"

    # Criar diretório de logs se não existir
    LOGS_DIR = BASE_DIR / "logs"
    LOGS_DIR.mkdir(exist_ok=True)

    # Configuração de logging
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {
                "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
                "style": "{",
            },
            "simple": {
                "format": "[{asctime}] {levelname} {message}",
                "style": "{",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "filters": {
            "require_debug_true": {
                "()": "django.utils.log.RequireDebugTrue",
            },
            "require_debug_false": {
                "()": "django.utils.log.RequireDebugFalse",
            },
        },
        "handlers": {
            "console": {
                "level": "INFO",
                "filters": ["require_debug_true"],
                "class": "logging.StreamHandler",
                "formatter": "simple",
            },
            "file_debug": {
                "level": "DEBUG",
                "class": "logging.FileHandler",
                "filename": str(LOGS_DIR / "debug.log"),
                "formatter": "verbose",
            },
            "file_error": {
                "level": "ERROR",
                "class": "logging.FileHandler",
                "filename": str(LOGS_DIR / "error.log"),
                "formatter": "verbose",
            },
            "security": {
                "level": "INFO",
                "class": "logging.FileHandler",
                "filename": str(LOGS_DIR / "security.log"),
                "formatter": "verbose",
            },
            "mail_admins": {
                "level": "ERROR",
                "filters": ["require_debug_false"],
                "class": "django.utils.log.AdminEmailHandler",
                "formatter": "verbose",
            },
        },
        "loggers": {
            "django": {
                "handlers": ["console", "file_debug"],
                "level": "INFO",
                "propagate": True,
            },
            "django.request": {
                "handlers": ["file_error", "mail_admins"],
                "level": "ERROR",
                "propagate": False,
            },
            "django.security": {
                "handlers": ["security", "mail_admins"],
                "level": "INFO",
                "propagate": False,
            },
            "accounts": {
                "handlers": ["console", "file_debug", "file_error"],
                "level": "INFO",
                "propagate": True,
            },
        },
    }

    # Verifica se as configurações mínimas estão presentes
    if "DATABASES" not in locals():
        raise ImportError("DATABASES configuration is missing")

    MAX_FAILED_LOGIN_ATTEMPTS = 50
    SIREN_LENGTH = 9
    VAT_NUMBER_LENGTH = 14
    APE_CODE_LENGTH = 5
