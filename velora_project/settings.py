"""Settings minimi del progetto host velora_project.

Questo file contiene la configurazione minima necessaria per far girare il
progetto Django host che ospita l'app `velora_ui` (il pacchetto distribuito) e
l'app `showcase` (la living styleguide). Le variabili sensibili e specifiche
dell'ambiente vengono lette da `.env` tramite `django-environ`, in modo che
sviluppo locale e produzione differiscano solo per il file env, non per il
codice. Vedi `.env.example` per i valori di default in dev.
"""

from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DJANGO_DEBUG=(bool, False),
)
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("DJANGO_SECRET_KEY", default="dev-not-secret-change-me")
DEBUG = env.bool("DJANGO_DEBUG", default=False)
ALLOWED_HOSTS = env.list(
    "DJANGO_ALLOWED_HOSTS",
    default=["velora.local", "localhost", "127.0.0.1"],
)

# Origini HTTPS attendibili per CSRF (reverse proxy / Traefik). Lista separata da virgola;
# es.: https://velora.example.com,https://www.velora.example.com
CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])

_django_env = env("DJANGO_ENV", default="dev")
if _django_env == "prod":
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    USE_X_FORWARDED_HOST = True

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "velora_ui.apps.VeloraUiConfig",
    "showcase.apps.ShowcaseConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "velora_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.template.context_processors.i18n",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "velora_ui.context_processors.header_defaults",
            ],
        },
    },
]

WSGI_APPLICATION = "velora_project.wsgi.application"

DATABASES = {
    "default": env.db_url(
        "DATABASE_URL",
        default="sqlite:///data/db.sqlite3",
    ),
}

LANGUAGE_CODE = "it"
TIME_ZONE = "Europe/Rome"
USE_I18N = True
USE_TZ = True
LANGUAGES = [
    ("it", "Italiano"),
    ("en", "English"),
]
LOCALE_PATHS = [
    BASE_DIR / "src" / "velora_ui" / "locale",
    BASE_DIR / "showcase" / "locale",
]

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
# Gli asset del pacchetto stanno in velora_ui/static/ (AppDirectoriesFinder).
# Non aggiungere lo stesso tree in STATICFILES_DIRS: collectstatic duplicherebbe ogni file
# (avvisi «Found another file with the destination path…» in produzione).

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
