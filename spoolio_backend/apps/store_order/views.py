from rest_framework import viewsets, filters
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response

from . import models, serializers

from ...libs import views as common_views, permissions as common_permissions


class StoreOrderViewSet(viewsets.ModelViewSet):

    queryset = models.StoreOrder.objects.all()
    serializer_class = serializers.StoreOrderSerializer
    permission_classes = (common_views.ActionBasedPermission,)
    pagination_class = LimitOffsetPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    action_permissions = {
        IsAdminUser: ['update', 'destroy'],
        common_permissions.IsAdminOrSelf: [],
        IsAuthenticated: ['retrieve', 'list', 'partial_update'],
        AllowAny: ['create']
    }

    def get_queryset(self):
        return models.StoreOrder.objects.filter(user_profile__user=self.request.user)


class StoreOrderUnitViewSet(viewsets.ModelViewSet):

    queryset = models.StoreOrderUnit.objects.all()
    serializer_class = serializers.StoreOrderUnitSerializer
    permission_classes = (common_views.ActionBasedPermission,)
    
    action_permissions = {
        IsAdminUser: ['update', 'partial_update', 'destroy'],
        common_permissions.IsAdminOrSelf: [],
        IsAuthenticated: ['retrieve', 'list'],
        AllowAny: ['create']
    }