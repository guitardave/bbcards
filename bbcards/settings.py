import os
import sys
from pathlib import Path
import django_heroku
import dj_database_url


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env if present
env_file = BASE_DIR / '.env'
if env_file.is_file():
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, val = line.split('=', 1)
            key = key.strip()
            val = val.strip().strip("'").strip('"')
            if key and key not in os.environ:
                os.environ[key] = val


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# ALLOWED_HOSTS and CSRF_TRUSTED_ORIGINS are set at the bottom of this file, after
# django_heroku.settings() runs, because it overwrites ALLOWED_HOSTS.

# CORS is only needed for the REST API. Allowed origins: jojodave.com and any subdomain (hyphens included).
CORS_URLS_REGEX = r'^/api/.*$'
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://([\w-]+\.)?jojodave\.com$",
]
if DEBUG:
    CORS_ALLOWED_ORIGINS = ['http://localhost:8000', 'http://127.0.0.1:8000']

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

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ]
}


# Application definition

INSTALLED_APPS = [
    'api.apps.ApiConfig',
    'cards.apps.CardsConfig',
    'players.apps.PlayersConfig',
    'users.apps.UsersConfig',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'storages',
    'crispy_forms',
    'crispy_bootstrap4',
    'crispy_bootstrap5',
    'django_bcrypt',
    'django_bootstrap_breadcrumbs',
    'django_bootstrap5',
    'django_htmx',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bbcards.urls'

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
                'cards.custom_context_processor.copyright_year_ctx',
                'cards.custom_context_processor.cards_count_ctx',
                'cards.custom_context_processor.card_sets_list_ctx',
                'cards.custom_context_processor.player_list_ctx',
                'users.custom_context_processor.toggle_mode_ctx',
                'users.custom_context_processor.user_full_name_ctx',

            ],
        },
    },
]

WSGI_APPLICATION = 'bbcards.wsgi.application'

# Login

LOGIN_URL = 'users:login'

# Databases

if 'test' in sys.argv or 'pytest' in sys.modules or os.getenv('DJANGO_TESTING') == '1':
    if os.getenv("DATABASE_URL") and "sqlite" in os.getenv("DATABASE_URL"):
        DATABASES = {
            "default": dj_database_url.parse(os.getenv("DATABASE_URL")),
        }
    elif os.getenv("TEST_DATABASE_URL"):
        DATABASES = {
            "default": dj_database_url.parse(os.getenv("TEST_DATABASE_URL")),
        }
    else:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'test_db.sqlite3',
            }
        }
else:
    if os.getenv("DATABASE_URL", None) is None:
        raise Exception("DATABASE_URL environment variable not defined")
    DATABASES = {
        "default": dj_database_url.parse(os.getenv("DATABASE_URL")),
    }

REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PORT = os.environ.get('REDIS_PORT')
REDIS_USER = os.environ.get('REDIS_USER')
REDIS_PW = os.environ.get('REDIS_PW')

REDIS_URI = f'rediss://{REDIS_USER}:{REDIS_PW}@{REDIS_HOST}:{REDIS_PORT}'


# Caching

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URI,
        "KEY_PREFIX": "bbcards",
        "TIMEOUT": 60 * 15,  # in seconds: 60 * 15 (15 minutes)
    }
}


# Password validation

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

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.CryptPasswordHasher',
)


# Internationalization

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Phoenix'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# AWS access information for S3 bucket

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_QUERYSTRING_AUTH = False
AWS_LOCATION = 'static'
AWS_S3_FILE_OVERWRITE = False
AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400',}
AWS_DEFAULT_ACL = None

PUBLIC_MEDIA_LOCATION = 'media'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)


# Uploaded media (card images) goes to S3 when a bucket is configured, otherwise to local disk.
# Local disk is ephemeral on most deploy targets, so production should always set the AWS_* vars.
AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME')
AWS_S3_ENDPOINT_URL = os.environ.get('AWS_S3_ENDPOINT_URL')  # only for S3-compatible hosts (e.g. DO Spaces)

if AWS_STORAGE_BUCKET_NAME and AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
    STORAGES = {
        'default': {
            'BACKEND': 'storages.backends.s3.S3Storage',
            'OPTIONS': {'location': PUBLIC_MEDIA_LOCATION},
        },
        'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage'},
    }
    MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{PUBLIC_MEDIA_LOCATION}/'
else:
    STORAGES = {
        'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage'},
    }
    MEDIA_URL = '/media/'
STATIC_URL = '/static/'


CRISPY_TEMPLATE_PACK = 'bootstrap5'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# AI image agent (DigitalOcean Serverless Inference + Brave Image Search)

MODEL_ACCESS_KEY = os.environ.get('MODEL_ACCESS_KEY')
DO_INFERENCE_URL = os.environ.get('DO_INFERENCE_URL', 'https://inference.do-ai.run/v1')
DO_INFERENCE_MODEL = os.environ.get('DO_INFERENCE_MODEL', 'deepseek-v4.1-flash')
BRAVE_API_KEY = os.environ.get('BRAVE_API_KEY')

# General

DEFAULT_LIMIT = 50

django_heroku.settings(locals(), databases=False, test_runner=False, staticfiles=False)


# Hosts and HTTPS
# Set after django_heroku.settings(), which would otherwise replace ALLOWED_HOSTS with ['*'].
# Comma-separated; override with DJANGO_ALLOWED_HOSTS. '.jojodave.com' matches the apex and all subdomains.
ALLOWED_HOSTS = [
    h.strip() for h in os.environ.get('ALLOWED_HOSTS', '.jojodave.com').split(',') if h.strip()
]
# Full origins incl. scheme; override with DJANGO_CSRF_TRUSTED_ORIGINS. Wildcards don't match the apex, so list both.
CSRF_TRUSTED_ORIGINS = [
    o.strip()
    for o in os.environ.get('DJANGO_CSRF_TRUSTED_ORIGINS', 'https://jojodave.com,https://*.jojodave.com').split(',')
    if o.strip()
]

if not DEBUG:
    # Assumes TLS is terminated by a trusted proxy / load balancer that sets X-Forwarded-Proto.
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = os.environ.get('DJANGO_SSL_REDIRECT', 'True').lower() == 'true'
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    # Leave at 0 until HTTPS is confirmed working; HSTS is hard to undo once browsers cache it.
    SECURE_HSTS_SECONDS = int(os.environ.get('DJANGO_HSTS_SECONDS', '0'))
