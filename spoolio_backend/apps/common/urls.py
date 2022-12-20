from django.urls import path, include

from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register('comments', views.CommentViewSet)
router.register('likes', views.LikeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]