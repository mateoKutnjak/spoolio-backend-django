from django.urls import path, include

from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register('print-jobs', views.PrintingJobViewSet)

urlpatterns = [
    path('', include(router.urls)),
]