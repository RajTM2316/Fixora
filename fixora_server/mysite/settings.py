from dotenv import load_dotenv
load_dotenv() 

from pathlib import Path
import os

from dotenv import load_dotenv
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


# =========================
# SECURITY
# =========================

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

DEBUG = os.getenv("DEBUG") == "True"

ALLOWED_HOSTS = []


# =========================
# APPLICATIONS
# =========================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Fixora Apps
    'manage_user',
    'manage_service',
    'payments',
    'channels',
    'chat',
]


# =========================
# MIDDLEWARE
# =========================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# =========================
# URL / TEMPLATE
# =========================

ROOT_URLCONF = 'mysite.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'mysite.wsgi.application'
ASGI_APPLICATION = 'mysite.asgi.application'


# =========================
# DATABASE
# =========================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'fixora',
        'USER': 'postgres',
        'PASSWORD': '2316',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


# =========================
# PASSWORD VALIDATION
# =========================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# =========================
# INTERNATIONALIZATION
# =========================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# =========================
# STATIC & MEDIA
# =========================

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"  # Required for production collectstatic

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# =========================
# AUTH REDIRECTS
# =========================

LOGIN_URL = "login"   # Named URL recommended
LOGIN_REDIRECT_URL = "/manage_service/home/"
LOGOUT_REDIRECT_URL = "/"


# =========================
# CHANNELS
# =========================

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}


# =========================
# SESSION SETTINGS
# =========================

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 3600  # 1 hour

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")