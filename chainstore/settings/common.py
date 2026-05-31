import os
from pathlib import Path
from datetime import timedelta
import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Initialize the environment reader
env = environ.Env()
environ.Env.read_env(BASE_DIR / '.env')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.sessions',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_filters',
    'corsheaders',
    'rest_framework',
    'drf_spectacular',
    'djoser',
    'cloudinary',
    'cloudinary_storage',
    'store',
    'core',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]

ROOT_URLCONF = 'chainstore.urls'

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

WSGI_APPLICATION = 'chainstore.wsgi.application'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'COERCE_DECIMAL_TO_STRING': False,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'E-Commerce ChainStore API',
    'DESCRIPTION': 'Complete backend API with Stripe Fiat and MetaMask Web3 Payment Integrations.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SERVE_PERMISSIONS': ['rest_framework.permissions.AllowAny'],
    'COMPONENT_SPLIT_PATCH': True,
    'COMPONENT_SPLIT_REQUEST': True,
}

AUTH_USER_MODEL = 'core.User'

DJOSER = {
    'SERIALIZERS': {
        'user_create': 'core.serializers.UserCreateSerializer',
        'current_user': 'core.serializers.UserSerializer',
    },
    # FIX FOR ERROR 1: Tell Djoser we use JWTs, so don't look for DB tokens
    'TOKEN_MODEL': None,

    # FIX FOR ERROR 2: Tell Djoser what the frontend reset link looks like
    'PASSWORD_RESET_CONFIRM_URL': 'password/reset/confirm/{uid}/{token}',

    # Optional but recommended: Require users to type their current password
    # to change their email or password (prevents hackers from hijacking logged-in sessions)
    'PASSWORD_CHANGED_EMAIL_CONFIRMATION': True,
}


EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

SIMPLE_JWT = {
    'AUTH_HEADER_TYPES': ('JWT',),
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1)
}

# --- PAYMENT GATEWAY CONFIGURATIONS ---
STRIPE_PUBLIC_KEY = env('STRIPE_PUBLIC_KEY')
STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = env('STRIPE_WEBHOOK_SECRET', default='')

WEB3_PROVIDER_URI = env('WEB3_PROVIDER_URI',
                        default='https://ethereum-sepolia-rpc.publicnode.com')
