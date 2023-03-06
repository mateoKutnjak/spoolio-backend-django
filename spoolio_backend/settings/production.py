from decouple import Config, RepositoryEnv

from .base import *

env_file = os.path.join(BASE_DIR, '.env.production')
env_config = Config(RepositoryEnv(env_file))

env_file_db = os.path.join(BASE_DIR, '.env.production.db')
env_config_db = Config(RepositoryEnv(env_file_db))

SECRET_KEY = env_config('SECRET_KEY')

DEBUG = False

ALLOWED_HOSTS = ['localhost', 'spoolio.net']

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