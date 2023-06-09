from django.urls import path, include

from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register('orders', views.ModelingOrderViewSet)
router.register('item-types', views.ItemTypeViewSet)
router.register('item-attributes', views.ItemAttributeViewSet)

urlpatterns = [
    path('modeling-orders/', include(router.urls)),
]