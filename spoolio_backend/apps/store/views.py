from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny

from . import models, serializers

from ...libs import views as common_views


class ProductViewSet(viewsets.ModelViewSet):

    queryset = models.Product.objects.all()
    serializer_class = serializers.ProductSerializer
    permission_classes = (common_views.ActionBasedPermission,)
    pagination_class = LimitOffsetPagination

    action_permissions = {
        IsAdminUser: ['create', 'update', 'partial_update', 'destroy'],
        IsAuthenticated: [],
        AllowAny: [ 'retrieve', 'list']
    }