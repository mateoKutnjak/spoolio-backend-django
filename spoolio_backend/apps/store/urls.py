from django.urls import path, include

from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register('product-categories', views.ProductCategoryViewSet)
router.register('product-subcategories', views.ProductSubcategoryViewSet)
router.register('products', views.ProductViewSet)
router.register('product-variations', views.ProductVariationViewSet)
router.register('product-variation-options', views.ProductVariationOptionViewSet)
router.register('product-variation-option-combinations', views.ProductVariationOptionCombinationViewSet)


urlpatterns = [
    path('', include(router.urls)),
]