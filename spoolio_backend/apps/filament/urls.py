from django.urls import path, include

from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register('colors', views.ColorViewSet)
router.register('materials', views.MaterialViewSet)
router.register('infills', views.InfillViewSet)
router.register('spools', views.SpoolViewSet)


urlpatterns = [
    path('filament/', include(router.urls)),
]