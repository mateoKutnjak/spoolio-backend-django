from django.urls import path, include

from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register('blogs', views.BlogViewSet)
router.register('categories', views.CategoryViewSet)
router.register('subcategories', views.SubcategoryViewSet)
router.register('tags', views.TagViewSet)

urlpatterns = [
    path('blog/', include(router.urls)),
]