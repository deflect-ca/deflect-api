"""
Django settings for core project.

Generated by 'django-admin startproject' using Django 3.1.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
from pathlib import Path

import os
import json
import environ

env = environ.Env(
    ALLOWED_HOSTS=(list, []),
    USE_SQLITE=bool,
    TESTING=bool
)

# Use .env.ci instead of .env during CI test
ENV_PATH = os.environ['ENV_PATH'] if 'ENV_PATH' in os.environ else None
environ.Env.read_env(env_file=ENV_PATH)
TESTING = env('TESTING', default=False)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG', default=False)

ALLOWED_HOSTS = env('ALLOWED_HOSTS')


# Application definition

INSTALLED_APPS = [
    'rest_framework',
    'rest_framework.authtoken',
    'api.apps.ApiConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_celery_results'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

if 'USE_SQLITE' in os.environ or env('USE_SQLITE', default=False):
    # Use sqlite in CI test, defined in test.py
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3'
        }
    }
else:
    # Ordinary database setup
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': env('DB_NAME', default='deflect-core'),
            'USER': env('DB_USER'),
            'PASSWORD': env('DB_PASSWORD'),
            'HOST': env('DB_HOST', default='localhost'),
            'PORT': env('DB_PORT', default='5432'),
        }
    }

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = env('TIME_ZONE', default='UTC')

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static")

# Custom
APP_NAME = env('APP_NAME', default='deflect-core')

# Edgemanage
EDGEMANAGE_CONFIG = env('EDGEMANAGE_CONFIG')
EDGEMANAGE_DNET = env('EDGEMANAGE_DNET')
EDGEMANAGE_TEST_EDGE = env('EDGEMANAGE_TEST_EDGE', default='deflect.ca')

COLOR_LOG_SCHEMA = {
    'DEBUG':    'cyan',
    'INFO':     'green',
    'WARNING':  'yellow',
    'ERROR':    'red',
    'CRITICAL': 'red,bg_white',
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'normal': {
            'format': '[%(levelname)s] %(asctime)s (%(name)s:%(lineno)d): %(message)s'
        },
        'simple': {
            'format': '[%(levelname)s] %(message)s'
        },
        'normal-color': {
            '()': 'colorlog.ColoredFormatter',
            'format': '%(log_color)s%(levelname)s | %(asctime)s (%(name)s:%(lineno)d): %(message)s',
            'log_colors': COLOR_LOG_SCHEMA,
        },
        'simple-color': {
            '()': 'colorlog.ColoredFormatter',
            'format': '%(log_color)s%(levelname)s (%(name)s:%(lineno)d) | %(message)s',
            'log_colors': COLOR_LOG_SCHEMA,
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple-color'
        },
        'file': {
            'level': env('DEBUG_LOG_FILE_LEVEL', default='INFO'),
            'class': 'logging.FileHandler',
            'filename': env('DEBUG_LOG_FILE_PATH', default='dev/logs/debug.log'),
            'formatter': 'normal'
        },
        'file-sql': {
            'class': 'logging.FileHandler',
            'filename': env('DEBUG_LOG_SQL_FILE_PATH', default='dev/logs/sql.log'),
            'formatter': 'normal'
        },
    },
    'loggers': {
        '': {
            'level': env('DEBUG_LOG_LEVEL', default='INFO'),
            'handlers': ['console', 'file'],
        },
        'django.db.backends': {
            'level': env('DEBUG_LOG_SQL_LEVEL', default='INFO'),
            'handlers': ['file-sql'],
            'propagate': False,
        }
    }
}

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
        #'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'api.auth.TokenAuthenticationChild',
        'rest_framework.authentication.SessionAuthentication',  # API viewer
    ]
}

GSC_LOG_FILE = env('GSC_LOG_FILE', default="/var/tmp/gen_site_config.log")
GSC_OUTPUT_FILE = env('GSC_OUTPUT_FILE', default="{}.site.yml")
GSC_OUTPUT_LOCATION = env('GSC_OUTPUT_LOCATION', default="/var/www/brainsconfig")
GSC_PARTITIONS = json.loads(env('GSC_PARTITIONS'))
GSC_BLACKLIST_FILE = env('GSC_BLACKLIST_FILE', default='blacklist.txt')
GSC_DEFAULT_CACHE_TIME = env('GSC_DEFAULT_CACHE_TIME', default=10)
GSC_DEFAULT_NETWORK = env('GSC_DEFAULT_NETWORK', default='dnet1')
GSC_REMAP_PURGE_DEFAULT_SECRET = env('GSC_REMAP_PURGE_DEFAULT_SECRET', default='some-dummy-secret')
GSC_IGNORE_APPROVAL = env('GSC_IGNORE_APPROVAL', default=True)  # deflect-web legacy
GSC_TRIGGER_UPON_DB_CHANGE = env('GSC_TRIGGER_UPON_DB_CHANGE', default=False)

# Celery
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='amqp://localhost')
CELERY_RESULT_BACKEND = 'django-db'
