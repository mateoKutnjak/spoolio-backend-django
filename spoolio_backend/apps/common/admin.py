from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from . import models


class AttachmentFileAdmin(GenericTabularInline):
    model = models.AttachmentFile
    extra = 0


class AttachmentImageAdmin(GenericTabularInline):
    model = models.AttachmentImage
    extra = 0


admin.site.register(models.Comment)
admin.site.register(models.Like)
admin.site.register(models.ShippingAddress)
admin.site.register(models.BillingAddress)
admin.site.register(models.AttachmentFile)
admin.site.register(models.AttachmentImage)
admin.site.register(models.ShippingMethod)