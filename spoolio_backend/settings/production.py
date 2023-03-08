from decouple import Config, RepositoryEnv

from .base import *


env_file = os.path.join(BASE_DIR, '.env.production')
env_config = Config(RepositoryEnv(env_file))

env_file_db = os.path.join(BASE_DIR, '.env.production.db')
env_config_db = Config(RepositoryEnv(env_file_db))

SECRET_KEY = env_config('SECRET_KEY')

DEBUG = False

ALLOWED_HOSTS = ['*'] # TODO cahnge this later, old values: ['localhost', 'spoolio.net']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME':env_config_db('POSTGRES_NAME'),
        'USER': env_config_db('POSTGRES_USER'),
        'PASSWORD': env_config_db('POSTGRES_PASSWORD'),
        'HOST': env_config_db('POSTGRES_HOST'),
        'PORT': env_config_db('POSTGRES_PORT', cast=int)
    }
}

DBBACKUP_STORAGE = "django.core.files.storage.FileSystemStorage"
DBBACKUP_STORAGE_OPTIONS = {
    "location": "backups/"
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

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
