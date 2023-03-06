from decouple import config

from .base import *

is_production = config('PRODUCTION', default=False, cast=bool)

if is_production:
   from .production import *
else:
   from .development import *