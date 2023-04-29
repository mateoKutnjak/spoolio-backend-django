from django.contrib import admin

from . import models

admin.site.register(models.Category)
admin.site.register(models.Subcategory)
admin.site.register(models.Tag)
admin.site.register(models.Blog)