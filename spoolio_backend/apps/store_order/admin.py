from django.contrib import admin

from . import models


class StoreOrderUnitInline(admin.TabularInline):
    model = models.StoreOrderUnit
    extra = 5


class StoreOrderAdmin(admin.ModelAdmin):
    inlines = (StoreOrderUnitInline,)


admin.site.register(models.StoreOrder, StoreOrderAdmin)
admin.site.register(models.StoreOrderUnit)