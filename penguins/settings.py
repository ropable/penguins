import os
import sys
import tomllib
from pathlib import Path
from zoneinfo import ZoneInfo

import dj_database_url
from dbca_utils.utils import env

# Project paths
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = str(Path(__file__).resolve().parents[1])
PROJECT_DIR = str(Path(__file__).resolve().parents[0])
# Add PROJECT_DIR to the system path.
sys.path.insert(0, PROJECT_DIR)

# Application definition
DEBUG = env("DEBUG", False)
SECRET_KEY = env("SECRET_KEY", "PlaceholderSecretKey")
CSRF_COOKIE_SECURE = env("CSRF_COOKIE_SECURE", False)
CSRF_TRUSTED_ORIGINS = env("CSRF_TRUSTED_ORIGINS", "http://127.0.0.1").split(",")
SESSION_COOKIE_SECURE = env("SESSION_COOKIE_SECURE", False)
SECURE_SSL_REDIRECT = env("SECURE_SSL_REDIRECT", False)
SECURE_REFERRER_POLICY = env("SECURE_REFERRER_POLICY", None)
SECURE_HSTS_SECONDS = env("SECURE_HSTS_SECONDS", 0)
if not DEBUG:
    ALLOWED_HOSTS = env("ALLOWED_HOSTS", "localhost").split(",")
else:
    ALLOWED_HOSTS = ["*"]
INTERNAL_IPS = ["127.0.0.1", "::1"]
ROOT_URLCONF = "penguins.urls"
WSGI_APPLICATION = "penguins.wsgi.application"
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
STORAGES = {
    "default": {
        # Use Azure storage as the default file backend.
        "BACKEND": "storages.backends.azure_storage.AzureStorage",
    },
    "staticfiles": {
        # Use whitenoise to add compression and caching support for static files.
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Application definition
INSTALLED_APPS = (
    "whitenoise.runserver_nostatic",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.gis",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
    "mapwidgets",
    "webtemplate_dbca",
    "observations",
)
MIDDLEWARE = [
    "penguins.middleware.HealthCheckMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "dbca_utils.middleware.SSOLoginMiddleware",
]
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(PROJECT_DIR, "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.template.context_processors.request",
                "django.template.context_processors.csrf",
                "django.contrib.messages.context_processors.messages",
                "penguins.context_processors.template_context",
            ],
        },
    },
]
# This is required to add context variables to all templates:
STATIC_CONTEXT_VARS = {}
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
pyproject = open(os.path.join(BASE_DIR, "pyproject.toml"), "rb")
project = tomllib.load(pyproject)
pyproject.close()
APPLICATION_VERSION_NO = project["project"]["version"]
SITE_TITLE = "Penguin Island Observations"
SITE_ACRONYM = "Penguins"
LOGOUT_URL = "/logout/"
LOGOUT_REDIRECT_URL = LOGOUT_URL
SITE_URL = env("SITE_URL", "localhost")
EXAMPLE_VIDEO_URL = env("EXAMPLE_VIDEO_URL", None)

# Email settings
EMAIL_HOST = env("EMAIL_HOST", "email.host")
EMAIL_PORT = env("EMAIL_PORT", 25)


# Database configuration
DATABASES = {
    # Defined in the DATABASE_URL env variable.
    "default": dj_database_url.config(),
}

DATABASES["default"]["TIME_ZONE"] = "Australia/Perth"
# Use PostgreSQL connection pool if using that DB engine (use ConnectionPool defaults).
if "ENGINE" in DATABASES["default"] and any(eng in DATABASES["default"]["ENGINE"] for eng in ["postgresql", "postgis"]):
    if "OPTIONS" in DATABASES["default"]:
        DATABASES["default"]["OPTIONS"]["pool"] = True
    else:
        DATABASES["default"]["OPTIONS"] = {"pool": True}

# Internationalization
TIME_ZONE = "Australia/Perth"
TZ = ZoneInfo(TIME_ZONE)
USE_TZ = True
USE_I18N = False
# Sensible AU date input formats
DATE_INPUT_FORMATS = (
    "%d/%m/%Y",
    "%d/%m/%y",
    "%d-%m-%Y",
    "%d-%m-%y",
    "%d %b %Y",
    "%d %b, %Y",
    "%d %B %Y",
    "%d %B, %Y",
    "%Y-%m-%d",  # Needed for form validation.
)

# Static files (CSS, JavaScript, Images)
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATIC_URL = "/static/"
WHITENOISE_ROOT = STATIC_ROOT

# Media uploads
MEDIA_URL = "/media/"

# Azure blob storage configuration
AZURE_ACCOUNT_NAME = os.environ.get("AZURE_ACCOUNT_NAME", None)
AZURE_ACCOUNT_KEY = os.environ.get("AZURE_ACCOUNT_KEY", None)
AZURE_CONTAINER = os.environ.get("AZURE_CONTAINER", None)


# Logging settings - log to stdout
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{asctime} {levelname} {name} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
            "stream": sys.stdout,
            "level": "WARNING",
        },
        "penguins": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
            "stream": sys.stdout,
            "level": "INFO",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "WARNING",
        },
        "penguins": {
            "handlers": ["penguins"],
            "level": "INFO",
        },
        # Set the logging level for all azure-* libraries (the azure-storage-blob library uses this one).
        # Reference: https://learn.microsoft.com/en-us/azure/developer/python/sdk/azure-sdk-logging
        "azure": {
            "handlers": ["console"],
            "level": "WARNING",
        },
    },
}

# django-map-widgets configuration
GEOSERVER_URL = env("GEOSERVER_URL", "")
LAYER_NAME = env("LAYER_NAME", "")
MAP_WIDGETS = {
    "Leaflet": {
        "PointField": {
            "interactive": {
                "mapOptions": {
                    "zoom": 16,
                    "scrollWheelZoom": True,
                    "zoomControl": True,
                    "attributionControl": False,
                },
                "tileLayer": {
                    "urlTemplate": f"{GEOSERVER_URL}/gwc/service/wmts?service=WMTS&request=GetTile&version=1.0.0&tilematrixset=mercator&tilematrix=mercator:{{z}}&tilecol={{x}}&tilerow={{y}}&format=image/png&layer={LAYER_NAME}",
                    "options": {"maxZoom": 22, "minZoom": 12},
                },
                "showZoomNavigation": True,
                "mapCenterLocation": (-32.305, 115.695),
            }
        }
    },
    "srid": 4326,
}
