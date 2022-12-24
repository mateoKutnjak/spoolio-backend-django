from django.urls import path, include

from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register('comments', views.CommentViewSet)
router.register('likes', views.LikeViewSet)
router.register('shipping-addresses', views.ShippingAddressViewSet)
router.register('billing-addresses', views.BillingAddressViewSet)

urlpatterns = [
    path('', include(router.urls)),
]