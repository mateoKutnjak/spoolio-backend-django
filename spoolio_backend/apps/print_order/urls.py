from django.urls import path, include

from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register('orders', views.PrintOrderViewSet)
router.register('units', views.PrintOrderUnitViewSet)
router.register('infills', views.PrintUnitInfillViewSet)
router.register('walls', views.PrintUnitWallViewSet)
router.register('infill-wall-combinations', views.PrintUnitInfillWallCombinationViewSet)

urlpatterns = [
    path('print-orders/', include(router.urls)),
]