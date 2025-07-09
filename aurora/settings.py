"""
Configuración de Django para el proyecto Aurora.

Este archivo contiene todas las configuraciones para el proyecto Aurora,
un sistema de gestión de empleados, proyectos y tareas.

Para más información sobre este archivo, consulta:
https://docs.djangoproject.com/en/4.2/topics/settings/

Para la lista completa de configuraciones y sus valores:
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ===================================
# CONFIGURACIÓN BÁSICA DEL PROYECTO
# ===================================

# Directorio base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Cargar variables de entorno desde el archivo .env
load_dotenv(BASE_DIR / '.env')

# Clave secreta para la seguridad criptográfica
# SECURITY WARNING: mantener la clave secreta en producción
SECRET_KEY = os.environ.get(
    'SECRET_KEY', 
    'django-insecure-default-key-change-this-in-production-immediately'
)

# Modo debug - NUNCA activar en producción
# SECURITY WARNING: no ejecutar con debug activado en producción
DEBUG = os.environ.get('DJANGO_DEBUG', 'False').lower() == 'true'

# Hosts permitidos para servir la aplicación
ALLOWED_HOSTS = [
    host.strip() 
    for host in os.environ.get(
        'DJANGO_ALLOWED_HOSTS', 
        'localhost,127.0.0.1,192.168.56.1'
    ).split(',')
]

# ===================================
# APLICACIONES INSTALADAS
# ===================================

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework.authtoken',
    'drf_yasg',
    'corsheaders',
]

LOCAL_APPS = [
    'app',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# Agregar debug toolbar solo en desarrollo
if DEBUG:
    INSTALLED_APPS.insert(0, 'debug_toolbar')

# ===================================
# MIDDLEWARE
# ===================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Agregar debug toolbar middleware solo en desarrollo
if DEBUG:
    MIDDLEWARE.insert(1, 'debug_toolbar.middleware.DebugToolbarMiddleware')

# ===================================
# CONFIGURACIÓN DE URLs Y TEMPLATES
# ===================================

ROOT_URLCONF = 'aurora.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

# ===================================
# CONFIGURACIÓN WSGI/ASGI
# ===================================

WSGI_APPLICATION = 'aurora.wsgi.application'
ASGI_APPLICATION = 'aurora.asgi.application'

# ===================================
# CONFIGURACIÓN DE BASE DE DATOS
# ===================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'aurora'),
        'USER': os.environ.get('DB_USER', 'aurora_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '3306'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
        'TEST': {
            'NAME': 'test_aurora',
            'CHARSET': 'utf8mb4',
            'COLLATION': 'utf8mb4_unicode_ci',
        },
    }
}

# Silenciar advertencias específicas de MySQL/MariaDB
SILENCED_SYSTEM_CHECKS = ['django.db.backends.mysql.W002']

# ===================================
# CONFIGURACIÓN DE DJANGO REST FRAMEWORK
# ===================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'EXCEPTION_HANDLER': 'app.exceptions.custom_exception_handler',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
}

# Agregar HTML renderer solo en desarrollo
if DEBUG:
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'].append(
        'rest_framework.renderers.BrowsableAPIRenderer'
    )

# ===================================
# CONFIGURACIÓN DE CORS
# ===================================

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",    # React development
    "http://localhost:5173",    # Vite development
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

CORS_ALLOW_CREDENTIALS = True

# ===================================
# VALIDADORES DE CONTRASEÑAS
# ===================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ===================================
# INTERNACIONALIZACIÓN
# ===================================

LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

# ===================================
# ARCHIVOS ESTÁTICOS Y MEDIA
# ===================================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Directorios adicionales para archivos estáticos
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# ===================================
# CONFIGURACIÓN DE SEGURIDAD
# ===================================

# Modelo de usuario personalizado
AUTH_USER_MODEL = 'app.Empleados'

# Configuraciones de seguridad adicionales para producción
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_REDIRECT_EXEMPT = []
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    X_FRAME_OPTIONS = 'DENY'

# ===================================
# CONFIGURACIÓN DE LOGGING
# ===================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'app': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}

# Crear directorio de logs si no existe
os.makedirs(BASE_DIR / 'logs', exist_ok=True)

# ===================================
# CONFIGURACIONES ESPECÍFICAS DE DEBUG
# ===================================

if DEBUG:
    # IPs internas para debug toolbar
    INTERNAL_IPS = [
        '127.0.0.1',
        'localhost',
    ]
    
    # Configuración adicional para desarrollo
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ===================================
# CONFIGURACIONES ADICIONALES
# ===================================

# Campo de clave primaria por defecto
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuración de URLs con slash final
APPEND_SLASH = True

# Configuración de sesiones
SESSION_COOKIE_AGE = 86400  # 24 horas
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# ===================================
# CONFIGURACIÓN DE CACHE (OPCIONAL)
# ===================================

# Descomenta para usar cache en producción
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.redis.RedisCache',
#         'LOCATION': 'redis://127.0.0.1:6379/1',
#     }
# }

# ===================================
# CONFIGURACIONES DE PRODUCCIÓN
# ===================================

# Configuraciones que se aplicarán solo en producción
if not DEBUG:
    # Configuración de email para producción
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.environ.get('EMAIL_HOST', '')
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
    DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@aurora.com')
    
    # Configuración adicional de seguridad
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    USE_X_FORWARDED_HOST = True
    USE_X_FORWARDED_PORT = True