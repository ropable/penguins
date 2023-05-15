import dj_database_url
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SECRET_KEY = os.environ.get('SECRET_KEY', 'PlaceholderSecretKey')
DEBUG = True if os.environ.get('DEBUG', False) == 'True' else False
CSRF_COOKIE_SECURE = True if os.environ.get('CSRF_COOKIE_SECURE', False) == 'True' else False
SESSION_COOKIE_SECURE = True if os.environ.get('SESSION_COOKIE_SECURE', False) == 'True' else False
if not DEBUG:
    ALLOWED_HOSTS = os.environ.get('ALLOWED_DOMAINS', 'localhost').split(',')
else:
    ALLOWED_HOSTS = ['*']
INTERNAL_IPS = ('127.0.0.1', '::1')
ROOT_URLCONF = 'penguins.urls'
WSGI_APPLICATION = 'penguins.wsgi.application'

# Email settings
ADMINS = ('asi@dbca.wa.gov.au',)
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp')
EMAIL_PORT = os.environ.get('EMAIL_PORT', 25)

# Application definition
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.humanize',
    'django.contrib.gis',
    'django_extensions',
    'daterange_filter',
    'datetimewidget',
    'south',
    'django_wsgiserver',
    'rest_framework',
    'leaflet',
    'observations'
)
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'penguins.middleware.SSOLoginMiddleware',
)

AUTH_USER_MODEL = "observations.PenguinUser"
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGIN_REDIRECT_URL_FAILURE = LOGIN_URL
LOGOUT_URL = '/logout/'
LOGOUT_REDIRECT_URL = LOGOUT_URL
ANONYMOUS_USER_ID = -1

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.core.context_processors.csrf',
    'django.core.context_processors.static',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'penguins.context_processors.from_settings',
)
TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )),
)
TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, "observations", "templates"),
)
TEMPLATE_DEBUG = DEBUG

# Database
DATABASES = {'default': dj_database_url.config()}
CONN_MAX_AGE = None

# Internationalization
SITE_ID = 1
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Australia/Perth'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# NOTE: don't remove media variables, even if unused.
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)


# Azure blob storage
DEFAULT_FILE_STORAGE = 'storages.backends.azure_storage.AzureStorage'
AZURE_ACCOUNT_NAME = os.environ.get('AZURE_ACCOUNT_NAME', None)
AZURE_ACCOUNT_KEY = os.environ.get('AZURE_ACCOUNT_KEY', None)
AZURE_CONTAINER = os.environ.get('AZURE_CONTAINER', None)


# Authentication
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)


# Misc settings
SOUTH_TESTS_MIGRATE = False
SKIP_SOUTH_TESTS = True
LEAFLET_CONFIG = {
    'SCALE': 'metric',
}
APPLICATION_VERSION_NO = '1.1.0'
SITE_URL = os.environ.get('SITE_URL', 'https://penguins.dbca.wa.gov.au')


# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'console': {'format': '%(asctime)s %(name)-12s %(message)s'},
        'standard': {
            'format': '%(asctime)-.19s [%(process)d] [%(levelname)s] %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'console'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': 'DEBUG'
        },
        'observations': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True
        },
        'videos': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True
        }
    }
}

if DEBUG:
    TEMPLATE_LOADERS = (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )
