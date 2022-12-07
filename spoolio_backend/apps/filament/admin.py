from django.contrib import admin

from . import models


admin.site.register(models.Color)
admin.site.register(models.Material)
admin.site.register(models.Infill)