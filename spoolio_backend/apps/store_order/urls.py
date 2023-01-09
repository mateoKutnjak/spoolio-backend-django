from django.urls import path, include

from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register('store-orders', views.StoreOrderViewSet)
router.register('store-order-units', views.StoreOrderUnitViewSet)


urlpatterns = [
    path('', include(router.urls)),
]