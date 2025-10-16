"""
Django settings for MyDjangoProjectServer project.
"""

import os
from pathlib import Path
from datetime import timedelta
import dj_database_url  # ✅ Importante: instala con pip install dj-database-url
from dotenv import load_dotenv

load_dotenv()  # ✅ Carga las variables del .env

BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------------
# 🔐 Seguridad
# -------------------------
SECRET_KEY = os.environ.get(
    'SECRET_KEY', 'django-insecure-(*e=$^3e0=%b7ty_p8qk!13w!$hl^qmvsynmkn+_&lsx*2&0jp'
)

DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# Render asigna un dominio automáticamente, así que permitimos todos
ALLOWED_HOSTS = ['*']

# -------------------------
# ⚙️ Aplicaciones
# -------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'clients',
    'authentication',
    'categories',
    'restaurants',
    'products',
    'address',
    'orders',
    'orderstatus',
]

# -------------------------
# 🔄 Middleware
# -------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # ✅ Para servir archivos estáticos en producción
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'MyDjangoProjectServer.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'MyDjangoProjectServer.wsgi.application'

# -------------------------
# 🗄️ Base de datos
# -------------------------
# ✅ Render leerá esta variable de entorno que apunte a tu base de Railway
DATABASES = {
    'default': dj_database_url.config(
        default='mysql://root:admin123@localhost:3306/restaurantedb',
        conn_max_age=600,
        ssl_require=False  # Railway no exige SSL
    )
}

# -------------------------
# 🔐 Autenticación y JWT
# -------------------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'authentication.customJWTAuthentication.CustomJWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=3),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# -------------------------
# 🌍 Internacionalización
# -------------------------
LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_TZ = True

# -------------------------
# 🖼️ Archivos estáticos y media
# -------------------------
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# -------------------------
# 🔧 Configuración extra
# -------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
CSRF_TRUSTED_ORIGINS = ['https://' + os.environ.get('RENDER_EXTERNAL_HOSTNAME', '')]
