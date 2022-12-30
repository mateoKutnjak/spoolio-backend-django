from django.contrib import admin

from . import models

from ..common import admin as common_admin


class ModelingOrderAdmin(admin.ModelAdmin):
    inlines = (common_admin.AttachmentFileAdmin, common_admin.AttachmentImageAdmin)


admin.site.register(models.ModelingOrder, ModelingOrderAdmin)
