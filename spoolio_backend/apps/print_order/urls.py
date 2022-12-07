from django.urls import path, include

from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register('orders', views.PrintOrderViewSet)
router.register('units', views.PrintOrderUnitViewSet)


urlpatterns = [
    path('print-orders/', include(router.urls)),
]