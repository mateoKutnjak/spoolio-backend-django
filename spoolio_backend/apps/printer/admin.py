from django.contrib import admin

from . import models


class PrinterInline(admin.StackedInline):
    model = models.Printer
    extra = 0


class PrinterTypeAdmin(admin.ModelAdmin):
    inlines = (PrinterInline, )


admin.site.register(models.PrinterType, PrinterTypeAdmin)
admin.site.register(models.Printer)