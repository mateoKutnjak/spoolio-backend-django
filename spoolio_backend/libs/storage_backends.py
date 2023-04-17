import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage

from decouple import Config, RepositoryEnv
from storages.backends.s3boto3 import S3Boto3Storage


if settings.DEBUG:
    env_filename = '.env.development'
    env_file = os.path.join(settings.BASE_DIR, env_filename)
    env_config = Config(RepositoryEnv(env_file))

    use_spaces = env_config('USE_SPACES', default=False, cast=bool)
else:
    use_spaces = True

if use_spaces:
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
    PublicMediaStorage = lambda: FileSystemStorage(location='media') 
    PrivateMediaStorage = lambda: FileSystemStorage(location='media')