"""
Django settings for MyDjangoProjectServer project.
"""

import os
from pathlib import Path
from datetime import timedelta
import dj_database_url
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
import cloudinary.api

load_dotenv()  # ✅ Carga las variables del .env

BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------------
# 🔐 Seguridad
# -------------------------
SECRET_KEY = os.environ.get(
    'SECRET_KEY', 'django-insecure-(*e=$^3e0=%b7ty_p8qk!13w!$hl^qmvsynmkn+_&lsx*2&0jp'
)

# ✅ En producción DEBUG debe ser False
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# ✅ Configuración para desarrollo y producción
if DEBUG:
    GLOBAL_IP = '192.168.100.13'
    GLOBAL_HOST = '3000'
    ALLOWED_HOSTS = [GLOBAL_IP, 'localhost', '127.0.0.1']
else:
    # Producción en Render
    ALLOWED_HOSTS = ['*']  # O especifica tu dominio de Render

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
    
    # ✅ Cloudinary DEBE ir antes de tus apps
    'cloudinary_storage',
    'cloudinary',
    
    # Tus apps
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
DATABASES = {
    'default': dj_database_url.config(
        default='mysql://root:admin123@localhost:3306/restaurantedb',
        conn_max_age=600,
        ssl_require=False
    )
}

# -------------------------
# ☁️ Cloudinary Configuration
# -------------------------
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME', ''),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY', ''),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET', ''),
}

# ✅ Configurar Cloudinary
cloudinary.config(
    cloud_name=CLOUDINARY_STORAGE['CLOUD_NAME'],
    api_key=CLOUDINARY_STORAGE['API_KEY'],
    api_secret=CLOUDINARY_STORAGE['API_SECRET'],
    secure=True
)

# ✅ Usar Cloudinary como almacenamiento por defecto para archivos media
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

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
# 🖼️ Archivos estáticos
# -------------------------
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ✅ Media files (ahora manejados por Cloudinary)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# -------------------------
# 🔧 Configuración extra
# -------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ✅ CSRF para Render
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS = [f'https://{RENDER_EXTERNAL_HOSTNAME}']

# -------------------------
# 🔒 Seguridad en producción
# -------------------------
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'