from django.contrib.auth.models import AnonymousUser

from rest_framework import viewsets, filters
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny

from . import models, serializers

from ...libs import views as common_views, permissions as common_permissions


class StoreOrderViewSet(viewsets.ModelViewSet, common_permissions.IsAdminOrObjectOwnerPermissionMixin):

    queryset = models.StoreOrder.objects.all()
    serializer_class = serializers.StoreOrderSerializer
    permission_classes = (common_views.ActionBasedPermission,)
    pagination_class = LimitOffsetPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    action_permissions = {
        IsAdminUser: ['update', 'destroy'],
        common_permissions.IsAdminOrSelf: ['retrieve', 'list', 'partial_update'],
        IsAuthenticated: [],
        AllowAny: ['create']
    }

    def get_queryset(self):
        # * As this method filters only order which belong to request.user,
        # * nobody else can perform any changes on this object
        return models.StoreOrder.objects.filter(user_profile__user=self.request.user)

    def get_object_owner(self, obj):
        if obj.user_profile:
            return obj.user_profile.user or AnonymousUser
        return AnonymousUser


class StoreOrderUnitViewSet(viewsets.ModelViewSet, common_permissions.IsAdminOrObjectOwnerPermissionMixin):

    queryset = models.StoreOrderUnit.objects.all()
    serializer_class = serializers.StoreOrderUnitSerializer
    permission_classes = (common_views.ActionBasedPermission,)
    
    action_permissions = {
        IsAdminUser: ['update', 'partial_update', 'destroy'],
        common_permissions.IsAdminOrSelf: ['retrieve', 'list'],
        IsAuthenticated: [],
        AllowAny: ['create']
    }

    def get_queryset(self):
        # * As this method filters only order which belong to request.user,
        # * nobody else can perform any changes on this object
        return models.StoreOrderUnit.objects.filter(order__user_profile__user=self.request.user)

    def get_object_owner(self, obj):
        if obj.user_profile:
            return obj.user_profile.user or AnonymousUser
        return AnonymousUser