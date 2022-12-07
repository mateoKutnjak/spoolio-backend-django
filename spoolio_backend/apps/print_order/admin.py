from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from . import models


class AttachmentFileAdmin(GenericTabularInline):
    model = models.AttachmentFile
    extra = 0


class AttachmentImageAdmin(GenericTabularInline):
    model = models.AttachmentImage
    extra = 0


class OrderUnitAdmin(admin.ModelAdmin):
    inlines = (AttachmentFileAdmin, AttachmentImageAdmin)


class OrderAdmin(admin.ModelAdmin):
    inlines = (AttachmentFileAdmin, AttachmentImageAdmin)


admin.site.register(models.AttachmentFile)
admin.site.register(models.AttachmentImage)

admin.site.register(models.OrderUnit, OrderUnitAdmin)

admin.site.register(models.PrintOrder, OrderAdmin)