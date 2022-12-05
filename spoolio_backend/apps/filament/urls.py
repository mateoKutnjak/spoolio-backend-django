from django.urls import path, include

from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register('colors', views.ColorViewSet)
router.register('materials', views.MaterialViewSet)


urlpatterns = [
    path('filament/', include(router.urls)),
]