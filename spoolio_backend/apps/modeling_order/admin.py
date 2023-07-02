from django.contrib import admin

from . import models

from ..common import admin as common_admin


class ModelingOrderAdmin(admin.ModelAdmin):
    inlines = (common_admin.AttachmentFileAdmin, common_admin.AttachmentImageAdmin)


admin.site.register(models.ModelingOrder, ModelingOrderAdmin)
admin.site.register(models.ItemAttribute)
admin.site.register(models.ItemType)
admin.site.register(models.OrderType)