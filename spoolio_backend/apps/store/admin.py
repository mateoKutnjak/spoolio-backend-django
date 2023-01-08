from django.contrib import admin

from . import models


admin.site.register(models.ProductCategory)
admin.site.register(models.ProductSubcategory)
admin.site.register(models.Product)
admin.site.register(models.ProductVariation)
admin.site.register(models.ProductVariationOption)
admin.site.register(models.ProductVariationOptionCombination)
admin.site.register(models.ProductImage)