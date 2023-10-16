from django.contrib import admin

from . import models

from ..common import admin as common_admin

import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_API_KEY


class OrderUnitInline(admin.StackedInline):
    model = models.OrderUnit
    extra = 0


class OrderUnitAdmin(admin.ModelAdmin):
    inlines = (common_admin.AttachmentFileAdmin,
               common_admin.AttachmentImageAdmin)


class OrderAdmin(admin.ModelAdmin):
    inlines = (OrderUnitInline, common_admin.AttachmentFileAdmin,
               common_admin.AttachmentImageAdmin)
    actions = ["accept_orders", "reject_orders"]

    @admin.action(description="Accept and charge orders")
    def accept_orders(self, request, queryset):
        for obj in queryset:
            payment_intent = obj.payment_intent
            if payment_intent:
                if len(payment_intent) > 3:
                    stripe.PaymentIntent.capture(payment_intent)

    @admin.action(description="Cancel payment and orders")
    def reject_orders(self, request, queryset):
        for obj in queryset:
            if obj.status == models.PrintOrder.STATUS_REVIEWING:
                obj.status = models.PrintOrder.STATUS_REJECTED
                obj.save()
                payment_intent = obj.payment_intent
                if payment_intent:
                    if len(payment_intent) > 3:
                        stripe.PaymentIntent.cancel(payment_intent)


admin.site.register(models.OrderUnit, OrderUnitAdmin)
admin.site.register(models.PrintOrder, OrderAdmin)

admin.site.register(models.PrintUnitInfill)
admin.site.register(models.PrintUnitWall)
admin.site.register(models.PrintUnitWallThickness)
admin.site.register(models.PrintUnitInfillWallCombination)

admin.site.register(models.CostVariables)
admin.site.register(models.QuantityMultiplier)
