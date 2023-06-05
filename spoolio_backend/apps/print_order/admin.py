from django.contrib import admin

from . import models

from ..common import admin as common_admin


class OrderUnitInline(admin.StackedInline):
    model = models.OrderUnit
    extra = 0


class OrderUnitAdmin(admin.ModelAdmin):
    inlines = (common_admin.AttachmentFileAdmin, common_admin.AttachmentImageAdmin)


class OrderAdmin(admin.ModelAdmin):
    inlines = (OrderUnitInline, common_admin.AttachmentFileAdmin, common_admin.AttachmentImageAdmin)


admin.site.register(models.OrderUnit, OrderUnitAdmin)
admin.site.register(models.PrintOrder, OrderAdmin)

admin.site.register(models.PrintUnitInfill)
admin.site.register(models.PrintUnitWall)
admin.site.register(models.PrintUnitInfillWallCombination)