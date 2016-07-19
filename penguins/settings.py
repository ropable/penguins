from confy import env, database
import os

# Project paths
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Application definition
DEBUG = env('DEBUG', False)
SECRET_KEY = env('SECRET_KEY')
S3_FOLDER = env('S3_FOLDER')
CSRF_COOKIE_SECURE = env('CSRF_COOKIE_SECURE', False)
SESSION_COOKIE_SECURE = env('SESSION_COOKIE_SECURE', False)
if not DEBUG:
    # Localhost, UAT and Production hosts
    ALLOWED_HOSTS = [
        'localhost',
        '127.0.0.1',
        'kens-xenmate-dev',
        'penguins.dpaw.wa.gov.au',
        'penguins.dpaw.wa.gov.au.',
        'penguins-test.dpaw.wa.gov.au',
        'penguins-test.dpaw.wa.gov.au.',
    ]
INTERNAL_IPS = ['127.0.0.1', '::1']
ROOT_URLCONF = 'penguins.urls'
WSGI_APPLICATION = 'penguins.wsgi.application'
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.flatpages',
    'markitup',
    'flatpages_x',
    'sorl.thumbnail',
    'django.contrib.sites',
    'django.contrib.humanize',
    'django.contrib.gis',
    'django_extensions',
    'debug_toolbar',
    'daterange_filter',
    'compressor',
    'datetimewidget',
    'south',
    'storages',
    'django_wsgiserver',
    'django_nose',
    'rest_framework',
    'leaflet',
    # actual app
    'observations'
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.core.context_processors.csrf',
    'django.core.context_processors.static',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'penguins.context_processors.standard',
)

# Email settings
ADMINS = ('asi@dpaw.wa.gov.au',)
EMAIL_HOST = env('EMAIL_HOST', 'email.host')
EMAIL_PORT = env('EMAIL_PORT', 25)

# Database configuration
DATABASES = {
    # Defined in the DATABASE_URL env variable.
    'default': database.config(),
}

# Internationalization
SITE_ID = 1
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Australia/Perth'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# Ensure that the media directory exists:
if not os.path.exists(os.path.join(BASE_DIR, 'media')):
    os.mkdir(os.path.join(BASE_DIR, 'media'))
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

if env('USE_AWS', False):
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
    AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_HOST = env('AWS_S3_HOST')
    AWS_QUERYSTRING_AUTH = False

FLATPAGES_X_PARSER = ["flatpages_x.markdown_parser.parse", {}]

TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )),
)

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, "observations", "templates"),
)

# Authentication
AUTH_USER_MODEL = "observations.PenguinUser"
from ldap_email_auth import ldap_default_settings
ldap_default_settings()
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'ldap_email_auth.auth.EmailBackend')
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGIN_REDIRECT_URL_FAILURE = LOGIN_URL
LOGOUT_URL = '/logout/'
LOGOUT_REDIRECT_URL = LOGOUT_URL
ANONYMOUS_USER_ID = -1


# Misc settings
COMPRESS_ENABLED = False
MARKITUP_SET = 'markitup/sets/markdown'
MARKITUP_SKIN = 'markitup/skins/markitup'
MARKITUP_FILTER = ('markdown.markdown', {'safe_mode': False})
SOUTH_TESTS_MIGRATE = False
SKIP_SOUTH_TESTS = True
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
LEAFLET_CONFIG = {
    'SCALE': 'metric',
}
# Application version number
APPLICATION_VERSION_NO = '1.0'

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s %(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/penguins.log'),
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 5,
            'formatter': 'standard',
        },
        'video_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/videos.log'),
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 5,
            'formatter': 'standard',
        },
    },
    'loggers': {
        'observations': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True
        },
        'videos': {
            'handlers': ['video_file'],
            'level': 'DEBUG',
            'propagate': True
        }
    }
}

if DEBUG:
    # Set up logging differently to give us some more information about what's
    # going on
    LOGGING['loggers'] = {
        'django_auth_ldap': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True
        },
        'django.request': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True
        },
        'observations': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True
        },
        'videos': {
            'handlers': ['video_file'],
            'level': 'DEBUG',
            'propagate': True
        }
    }

    TEMPLATE_LOADERS = (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )

    DEBUG_TOOLBAR_CONFIG = {
        'HIDE_DJANGO_SQL': False,
        'INTERCEPT_REDIRECTS': False,
    }
