"""
Django settings for backend project.

Generated by 'django-admin startproject' using Django 4.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import environ
import os

from corsheaders.defaults import default_headers

LOCAL_IP = "10.0.0.3"

env = environ.Env(
    DB_NAME=(str, 'transcendence'),
    DB_USER=(str, 'postgres'),
    DB_PASS=(str, 'password'),
    DB_HOST=(str, '127.0.0.1'),
    DB_PORT=(str, '5432'),
    MYPY_DJANGO_CONFIG=(str, './mypy.ini'),
    CORS_ALLOWED_ORIGINS=(list, ["http://localhost:8080", "http://localhost", "http://10.0.0.3:8080", "http://10.0.0.3:8000", "http://10.0.0.3:8080", "http://10.0.0.3:8000", f"http://{LOCAL_IP}:8080", f"http://{LOCAL_IP}:8000"]),
    JWT_SECRET=(str, 'SECRET'),
    PASSWORD_42AUTH=(str, ''),
    APP_NAME=(str, 'EpicPong'),
    CLIENT_ID=(str, "u-s4t2ud-ba30256e8d43ec186c62b98c28d1db0a9169d279f7e85d1a4daa5cb986af0b2b"),
    CLIENT_SECRET=(str, "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"),
    REDIRECT_URI=(str, "http://localhost:8000/authentication/42-register/"),
    AUTHORIZE_URL=(str, "https://api.intra.42.fr/oauth/authorize"),
    TOKEN_URL=(str, "https://api.intra.42.fr/oauth/token")
)

CORS_ALLOWED_ORIGINS = env('CORS_ALLOWED_ORIGINS')
CORS_ALLOW_HEADERS = [*default_headers, 'X-CSRFToken']
CORS_ALLOW_CREDENTIALS = True

UNAUTHENTICATED_REQUESTS = ['/authentication/login', '/authentication/register', '/server_info/', '/authentication/42-register/', '/authentication/login42']
UNAUTHENTICATED_2FA_REQUESTS = ['/authentication/check-code','/authentication/logout']

CSRF_TRUSTED_ORIGINS = ["http://localhost:8080", "http://localhost:8000", "http://10.0.0.3:8080", "http://10.0.0.3:8000", "http://10.0.0.3:8000", "http://10.0.0.3:8080", f"http://{LOCAL_IP}:8080", f"http://{LOCAL_IP}:8000"]
CSRF_COOKIE_DOMAIN = f"{LOCAL_IP}"

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-otc*6$yc^vbe&m1uzzt!0jt^l=4r4=q&3#voh5een44bu4v)u#'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1", "0.0.0.0", "localhost", "10.0.0.34", "10.0.0.3", "localhost", "0.0.0.0", f"{LOCAL_IP}"]

# Application definition
INSTALLED_APPS = [
    'daphne',
    'game',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django_extensions',
    'rest_framework',
    'corsheaders',

    'core',
    'friends',
    'blocks',
    'backend',
    'chats',
    'authentication',
    'tournament_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'authentication.middleware.CustomAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

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

WSGI_APPLICATION = 'backend.wsgi.application'
ASGI_APPLICATION = "backend.asgi.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASS'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE = 3600

AUTH_USER_MODEL = 'core.EpicPongUser'

AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend']
