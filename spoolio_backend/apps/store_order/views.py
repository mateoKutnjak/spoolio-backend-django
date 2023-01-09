from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response

from . import models, serializers

from ...libs import views as common_views, permissions as common_permissions


class StoreOrderViewSet(viewsets.ModelViewSet):

    queryset = models.StoreOrder.objects.all()
    serializer_class = serializers.StoreOrderCreateSerializer
    permission_classes = (common_views.ActionBasedPermission,)
    
    action_permissions = {
        IsAdminUser: ['update', 'partial_update', 'destroy'],
        common_permissions.IsAdminOrSelf: [],
        IsAuthenticated: ['retrieve', 'list'],
        AllowAny: ['create']
    }


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