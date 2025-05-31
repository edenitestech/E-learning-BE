# edenites_be/settings.py

import os
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

# ────────────────────────────────────────────────────────────────────────────────
# 1) LOAD ENVIRONMENT VARIABLES
# ────────────────────────────────────────────────────────────────────────────────
load_dotenv()  # this reads from .env in local development

# ────────────────────────────────────────────────────────────────────────────────
# 2) BASE DIRECTORY
# ────────────────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# ────────────────────────────────────────────────────────────────────────────────
# 3) DEBUG & SECRET KEY
# ────────────────────────────────────────────────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-hardcoded-key")
DEBUG      = os.getenv("DJANGO_DEBUG", "False") == "True"

# ────────────────────────────────────────────────────────────────────────────────
# 4) ALLOWED HOSTS
# ────────────────────────────────────────────────────────────────────────────────
# Comma-separated list in .env → split into Python list
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")
# e.g. ["127.0.0.1","localhost","e-learning-be-3n5m.onrender.com"]

# ────────────────────────────────────────────────────────────────────────────────
# 5) INSTALLED APPS
# ────────────────────────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    # Django core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third‐party libraries
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "django_extensions",
    "django_cryptography",

    # Your apps
    "accounts",
    "courses",
    "content",
    "enrollments",
    "exams",
]

# ────────────────────────────────────────────────────────────────────────────────
# 6) MIDDLEWARE
# ────────────────────────────────────────────────────────────────────────────────
MIDDLEWARE = [
    # CORS must come first
    "corsheaders.middleware.CorsMiddleware",

    # Security & static‐file serving
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",

    # Built‐in Django middleware
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "edenites_be.urls"

# ────────────────────────────────────────────────────────────────────────────────
# 7) TEMPLATES
# ────────────────────────────────────────────────────────────────────────────────
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],  # add any extra template directories here
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

WSGI_APPLICATION = "edenites_be.wsgi.application"

# ────────────────────────────────────────────────────────────────────────────────
# 8) DATABASE CONFIGURATION
# ────────────────────────────────────────────────────────────────────────────────
if DEBUG:
    # In DEBUG, prefer a local DATABASE_URL_LOCAL if set, else revert to SQLite
    local_db_url = os.getenv("DATABASE_URL_LOCAL", "").strip()
    if local_db_url:
        DATABASES = {
            "default": dj_database_url.parse(local_db_url, conn_max_age=600)
        }
    else:
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": BASE_DIR / "db.sqlite3",
            }
        }
else:
    # In production, use your Render Postgres URL (must be set in Render’s env)
    DATABASES = {
        "default": dj_database_url.parse(
            os.getenv("DATABASE_URL_PROD", ""),
            conn_max_age=600,
            ssl_require=True
        )
    }

# ────────────────────────────────────────────────────────────────────────────────
# 9) PAYMENT KEYS / DOMAIN
# ────────────────────────────────────────────────────────────────────────────────
PAYSTACK_SECRET_KEY    = os.getenv("PAYSTACK_SECRET_KEY")
PAYSTACK_PUBLIC_KEY    = os.getenv("PAYSTACK_PUBLIC_KEY")
PAYSTACK_WEBHOOK_SECRET = os.getenv("PAYSTACK_WEBHOOK_SECRET")
PAYSTACK_BASE_URL      = os.getenv("PAYSTACK_BASE_URL", "https://api.paystack.co")

# Use a single DOMAIN depending on DEBUG status
if DEBUG:
    DOMAIN = os.getenv("DOMAIN_LOCAL", "http://localhost:8000")
else:
    DOMAIN = os.getenv("DOMAIN_PROD", "https://e-learning-be-3n5m.onrender.com")

# ────────────────────────────────────────────────────────────────────────────────
# 10) AUTHENTICATION BACKENDS & SETTINGS
# ────────────────────────────────────────────────────────────────────────────────
AUTHENTICATION_BACKENDS = [
    "accounts.auth_backends.EmailOrUsernameBackend",
    "django.contrib.auth.backends.ModelBackend",
]
AUTH_USER_MODEL = "accounts.User"
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ────────────────────────────────────────────────────────────────────────────────
# 11) INTERNATIONALIZATION
# ────────────────────────────────────────────────────────────────────────────────
LANGUAGE_CODE = "en-us"
TIME_ZONE     = "UTC"
USE_I18N      = True
USE_TZ        = True

# ────────────────────────────────────────────────────────────────────────────────
# 12) STATIC & MEDIA FILES (WhiteNoise)
# ────────────────────────────────────────────────────────────────────────────────
STATIC_URL          = "/static/"
STATIC_ROOT         = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ────────────────────────────────────────────────────────────────────────────────
# 13) CORS CONFIGURATION
# ────────────────────────────────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
# e.g. ["http://localhost:3000","http://localhost:3002","https://edenlearn-fe.vercel.app"]
CORS_ALLOW_CREDENTIALS = True

# ────────────────────────────────────────────────────────────────────────────────
# 14) Django REST Framework
# ────────────────────────────────────────────────────────────────────────────────
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}

# ────────────────────────────────────────────────────────────────────────────────
# 15) SIMPLE JWT SETTINGS
# ────────────────────────────────────────────────────────────────────────────────
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME":  timedelta(minutes=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS":  True,
    "BLACKLIST_AFTER_ROTATION": True,
}

# ────────────────────────────────────────────────────────────────────────────────
# 16) SECURITY HARDENING
# ────────────────────────────────────────────────────────────────────────────────
if not DEBUG:
    SECURE_SSL_REDIRECT            = True
    SECURE_HSTS_SECONDS            = 60 * 60 * 24 * 365
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD            = True
    SESSION_COOKIE_SECURE          = True
    CSRF_COOKIE_SECURE             = True
else:
    SECURE_SSL_REDIRECT   = False
    SECURE_HSTS_SECONDS   = 0
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE    = False

X_FRAME_OPTIONS           = "DENY"
SECURE_BROWSER_XSS_FILTER = True

# ────────────────────────────────────────────────────────────────────────────────
# 17) LOGGING (console only)
# ────────────────────────────────────────────────────────────────────────────────
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": { "class": "logging.StreamHandler" }
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
