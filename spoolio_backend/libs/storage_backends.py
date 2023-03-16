import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage

from decouple import Config, RepositoryEnv
from storages.backends.s3boto3 import S3Boto3Storage


env_file = os.path.join(settings.BASE_DIR, '.env.development')
env_config = Config(RepositoryEnv(env_file))


if env_config('USE_SPACES', default=False, cast=bool):
    class StaticStorage(S3Boto3Storage):
        location = 'static'


    class PublicMediaStorage(S3Boto3Storage):
        location = 'media-public'
        file_overwrite = False


    class PrivateMediaStorage(S3Boto3Storage):
        location = 'media-private'
        default_acl = 'private'
        file_overwrite = False
        custom_domain = False

else:

    StaticStorage = lambda: FileSystemStorage(location='static') 
    PublicMediaStorage = lambda: FileSystemStorage(location='media-public') 
    PrivateMediaStorage = lambda: FileSystemStorage(location='media-private')