import os
from pathlib import Path
from decouple import config, Csv

# Construye rutas dentro del proyecto de esta manera: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ========== SEGURIDAD ==========
# ADVERTENCIA DE SEGURIDAD: ¡mantenga en secreto la clave secreta utilizada en producción!
SECRET_KEY = config('SECRET_KEY')

# ADVERTENCIA DE SEGURIDAD: ¡no ejecute con la depuración activada en producción!
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

# ========== APLICACIONES INSTALADAS ==========
# Organizadas por tipo: Django core, third-party, locales
INSTALLED_APPS = [
    # Django core apps
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',
    'channels',
    
    # Local apps (modulares)
    'users',        # Autenticación y perfiles
    'boards',       # Tableros, listas y tarjetas
    'notifications', # Sistema de notificaciones
    'activity',     # Registro de actividad reciente
    'websockets',   # Comunicación en tiempo real
    'comments',     # Comentarios en tarjetas
]

# ========== MIDDLEWARE ==========
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',  # Protección CSRF activada
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

# ========== TEMPLATES ==========
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Carpeta global de templates
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
ASGI_APPLICATION = 'core.asgi.application'  # Para Channels

# ========== BASE DE DATOS ==========
# SQLite para desarrollo, configurable vía .env para producción
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Redis
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
    },
}

# Validación de contraseñas robusta
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        'OPTIONS': {
            'user_attributes': ('username', 'email', 'first_name', 'last_name'),
            'max_similarity': 0.7,
        }
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
    # Validador personalizado para requisitos adicionales
    {
        'NAME': 'boards.validators.CustomPasswordValidator',
    },
]

# Configuración adicional de seguridad
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',  # Más seguro
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]

# ========== AUTENTICACIÓN ==========
# URLs de redirección
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

# ========== ARCHIVOS ESTÁTICOS Y MEDIA ==========
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ========== ZONA HORARIA ==========
# Importante: America/Asuncion asegura que todos los timestamps
# se almacenen y muestren en horario local de Paraguay
# Sin esto, Django usaría UTC y causaría desfases horarios
TIME_ZONE = 'America/Asuncion'
USE_TZ = True  # Usar zona horaria con soporte para horario de verano

# ========== IDIOMA ==========
LANGUAGE_CODE = 'es-py'

# ========== DEFAULT PRIMARY KEY ==========
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ========== SEGURIDAD ADICIONAL ==========
# Protección CSRF para APIs
CSRF_TRUSTED_ORIGINS = ['http://localhost:8000', 'http://127.0.0.1:8000']

# Configuración de sesiones
SESSION_COOKIE_AGE = 86400  # 24 horas
SESSION_COOKIE_SECURE = False  # True en producción con HTTPS
SESSION_COOKIE_HTTPONLY = True  # Previene acceso JavaScript a cookies
SESSION_COOKIE_SAMESITE = 'Lax'  # Protección CSRF adicional