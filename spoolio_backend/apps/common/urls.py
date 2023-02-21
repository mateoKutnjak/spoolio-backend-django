from django.urls import path, include

from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register('comments', views.CommentViewSet)
router.register('likes', views.LikeViewSet)
router.register('ratings', views.RatingViewSet)
router.register('shipping-addresses', views.ShippingAddressViewSet)
router.register('billing-addresses', views.BillingAddressViewSet)
router.register('attachment-files', views.AttachmentFileViewSet)
router.register('attachment-images', views.AttachmentImageViewSet)
router.register('shipping-methods', views.ShippingMethodViewSet)

urlpatterns = [
    path('', include(router.urls)),
]