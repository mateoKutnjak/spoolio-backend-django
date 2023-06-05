from django.urls import path, include

from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register('printers', views.PrinterViewSet)
router.register('printing-methods', views.PrintingMethodViewSet)

urlpatterns = [
    path('printers/', include(router.urls)),
]