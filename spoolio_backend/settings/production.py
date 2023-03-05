from decouple import Config, RepositoryEnv

from .base import *

dir_name = os.path.dirname(os.path.realpath(__file__))
env_file = os.path.join(dir_name, '.env.production')
env_config = Config(RepositoryEnv(env_file))

SECRET_KEY = env_config('SECRET_KEY')

DEBUG = False

ALLOWED_HOSTS = ['spoolio.net']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'spoolio_web_db',
        'USER': 'spoolio_web',
        'HOST': 'db',
        'PORT': 5432
    }
}