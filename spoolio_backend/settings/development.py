from decouple import Config, RepositoryEnv

from django.utils.log import DEFAULT_LOGGING

from .base import *
import logging.config


env_file = os.path.join(BASE_DIR, '.env.development')
env_config = Config(RepositoryEnv(env_file))

env_file_db = os.path.join(BASE_DIR, '.env.development.db')
env_config_db = Config(RepositoryEnv(env_file_db))

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

# SECURITY WARNING: don't run with debug turned on in production!
SECRET_KEY = env_config('SECRET_KEY')

DEBUG = True

ALLOWED_HOSTS = ['localhost', 'web']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env_config_db('POSTGRES_NAME'),
        'USER': env_config_db('POSTGRES_USER'),
        'PASSWORD': env_config_db('POSTGRES_PASSWORD'),
        'HOST': env_config_db('POSTGRES_HOST'),
        'PORT': env_config_db('POSTGRES_PORT', cast=int)
    }
}

# ****** CORS *******
CORS_ORIGIN_WHITELIST = [
    'http://localhost:3000'
]

CSRF_TRUSTED_ORIGINS = ['http://localhost:3000']

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

if env_config('USE_SPACES', default=False, cast=bool):

    # ****** Digital Ocean Spaces *******
    AWS_ACCESS_KEY_ID = env_config('SPACES_ACCESS_KEY')
    AWS_SECRET_ACCESS_KEY = env_config('SPACES_ACCESS_KEY_SECRET')

    AWS_STORAGE_BUCKET_NAME = 'spoolio'
    AWS_S3_ENDPOINT_URL = 'https://fra1.digitaloceanspaces.com'
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }

    AWS_DEFAULT_ACL = 'public-read'

    STATICFILES_STORAGE = 'spoolio_backend.libs.storage_backends.StaticStorage'

    STATIC_URL = '{}/{}/'.format(AWS_S3_ENDPOINT_URL, "static")

    DEFAULT_FILE_STORAGE = 'spoolio_backend.libs.storage_backends.PublicMediaStorage'
    PRIVATE_FILE_STORAGE = 'spoolio_backend.libs.storage_backends.PrivateMediaStorage'

else:

    # ****** Local media/static files *******
    STATIC_URL = 'static/'
    STATIC_ROOT = os.path.join(BASE_DIR, "static")

    MEDIA_URL = 'media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ****** Stripe *******
STRIPE_API_KEY = env_config('STRIPE_SECRET_KEY_TEST')

# ****** Django Channels ****** #
# ! DEVELOPMENT MODE:
# !
# ! Don't forget to run REDIS before starting Django
# ! server (in separate terminal) with command
# !
# ! docker run -ti -p 6379:6379 redis

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("redis", 6379)],
        },
    },
}

# ****** Celery[redis] ****** #
# ! DEVELOPMENT MODE:
# !
# ! Don't forget to run CELERY before starting Django
# ! server (in separate terminal) with command
# !
# ! celery -A spoolio_backend worker --loglevel=info --concurrency 1 -E
CELERY_BROKER_URL = "redis://redis:6379/0"
CELERY_RESULT_BACKEND = "redis://redis:6379/0"

# ****** Django-request ****** #
REQUEST_BASE_URL = 'http://localhost:8000'


now = datetime.datetime.now()
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'format': '%(levelname)s %(asctime)s %(message)s'
        },
        'file': {
            'format': '%(levelname)s %(asctime)s %(pathname)s (line %(lineno)d) %(message)s'
        },
        'django.server': DEFAULT_LOGGING['formatters']['django.server'],
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'console',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'formatter': 'file',
            'filename': str(BASE_DIR) + '/logs/' + ('DEV' if DEBUG else 'PROD') + now.strftime("-%Y-%m-%d") + '.log',
        },
        'django.server': DEFAULT_LOGGING['handlers']['django.server'],
    },
    'loggers': {
        '': {
            'level': 'INFO',
            'handlers': ['console', 'file']
        },
        'django.server': DEFAULT_LOGGING['loggers']['django.server'],
    }
})
