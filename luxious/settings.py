from django.utils.translation import gettext_lazy as _
import os
from pathlib import Path
from datetime import timedelta
from celery.schedules import crontab

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for Production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in Production secret!
SECRET_KEY = "jodUfHxtn-xiTr2c7_2D6hjaqhQ3o1voYE9ioVvKycNnWKALFzcs_EBIVex04I71G2M"

# SECURITY WARNING: don't run with debug turned on in Production!
DEBUG = True

ALLOWED_HOSTS = ['luxiousbeauty-land.com', 'www.luxiousbeauty-land.com', '127.0.0.1', 'localhost']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_celery_results',
    'django.contrib.humanize',
    'django_celery_beat',
    'rest_framework',
    'corsheaders',
    'core',
    'widget_tweaks',
]



MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
]

ROOT_URLCONF = 'luxious.urls'
AUTH_USER_MODEL = 'core.User'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
            ],
        },
    },
]


WSGI_APPLICATION = 'luxious.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Languages supported
LANGUAGES = [
    ('fr', _('Français')),
]

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/
# Static files (CSS, JavaScript, Images)
# Configuration des URLs de login/logout
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

# Configuration des fichiers statiques et médias
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

permission_required = 'auth.view_user'  # Par exemple

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Formats français
DATE_FORMAT = 'd/m/Y'
DATETIME_FORMAT = 'd/m/Y H:i'
TIME_FORMAT = 'H:i'
DATE_INPUT_FORMATS = ['%d/%m/%Y']
DATETIME_INPUT_FORMATS = ['%d/%m/%Y %H:%M']

SHORT_DATE_FORMAT = 'd/m/Y'
SHORT_DATETIME_FORMAT = 'd/m/Y H:i'

DECIMAL_SEPARATOR = ','
THOUSAND_SEPARATOR = ' '
USE_THOUSAND_SEPARATOR = True

CELERY_BEAT_SCHEDULE = {
    'check-overdue-credits': {
        'task': 'core.tasks.check_overdue_credits',
        'schedule': timedelta(days=1),  # Tous les jours
    },
    'check-low-stock': {
        'task': 'core.tasks.check_low_stock',
        'schedule': timedelta(hours=12),  # Toutes les 12 heures
    },
    'generate-daily-sales-report': {
        'task': 'core.tasks.generate_daily_sales_report',
        'schedule': crontab(hour=23, minute=30),  # Tous les jours à 23:30
    },
}

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'EXCEPTION_HANDLER': 'core.views.custom_exception_handler',
    
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}


# Configuration CORS
CORS_ALLOW_ALL_ORIGINS = False  # Mis à False pour la Production

# OU configuration plus sécurisée :
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://luxiousbeauty-land.com",
    "https://www.luxiousbeauty-land.com",
]

CORS_ALLOW_CREDENTIALS = True

# Si vous avez des problèmes avec les requêtes OPTIONS (preflight)
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# CSRF Configuration
CSRF_TRUSTED_ORIGINS = [
    'https://luxiousbeauty-land.com',
    'https://www.luxiousbeauty-land.com',
    'https://173.212.211.47'
]

# Email Configuration
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'votre-email@gmail.com'
EMAIL_HOST_PASSWORD = 'Elom1234'
DEFAULT_FROM_EMAIL = 'contact@luxiousbeauty-land.com'

# FedaPay Configuration
FEDAPAY_PUBLIC_KEY = 'pk_live_W2rHbWgvHU8xti08I6awZ5-k'
FEDAPAY_SECRET_KEY = 'sk_live_hjR_OMLAPBS4YMYYn7KdvQr2'
FEDAPAY_WEBHOOK_SECRET = 'wh_live_u1dDob_QpNm1oIUZrbYSC0FN'
FEDAPAY_ENVIRONMENT = 'live'
