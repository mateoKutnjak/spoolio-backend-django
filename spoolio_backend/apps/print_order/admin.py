from django.contrib import admin

from . import models


admin.site.register(models.AttachmentFile)
admin.site.register(models.AttachmentImage)

admin.site.register(models.OrderUnit)

admin.site.register(models.PrintOrder)