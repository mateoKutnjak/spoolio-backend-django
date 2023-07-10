from django.urls import path, include

from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register('blogs', views.BlogViewSet)
router.register('categories', views.CategoryViewSet)

urlpatterns = [
    path('faq/', include(router.urls)),
]