from decouple import Config, RepositoryEnv

from .base import *


env_file = os.path.join(BASE_DIR, '.env.development')
env_config = Config(RepositoryEnv(env_file))

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

# SECURITY WARNING: don't run with debug turned on in production!
SECRET_KEY = env_config('SECRET_KEY')

DEBUG = True

ALLOWED_HOSTS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
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

    MEDIA_URL = 'media-public/'
    MEDIA_ROOT  = os.path.join(BASE_DIR, 'media-public/')

    MEDIA_URL_1 = 'media-private/'
    MEDIA_ROOT_1  = os.path.join(BASE_DIR, 'media-private/')

# ****** Stripe ******* 
STRIPE_API_KEY = env_config('STRIPE_SECRET_KEY_TEST')