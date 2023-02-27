from rest_framework import filters, viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response

from . import models, serializers

from ...libs import views as common_views, permissions as common_permissions


class PrintOrderViewSet(viewsets.ModelViewSet):

    queryset = models.PrintOrder.objects.all()
    serializer_class = serializers.PrintOrderSerializer
    permission_classes = (common_views.ActionBasedPermission,)
    pagination_class = LimitOffsetPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    action_permissions = {
        IsAdminUser: ['destroy'],
        common_permissions.IsAdminOrSelf: ['retrieve', 'list', 'update', 'partial_update', ],
        AllowAny: ['create',]
    }

    def get_queryset(self):
        return models.PrintOrder.objects.filter(user_profile__user=self.request.user)


class PrintOrderUnitViewSet(viewsets.ModelViewSet):

    queryset = models.OrderUnit.objects.all()
    serializer_class = serializers.PrintOrderUnitSerializer
    permission_classes = (common_views.ActionBasedPermission,)
    pagination_class = LimitOffsetPagination

    action_permissions = {
        IsAdminUser: ['destroy'],
        common_permissions.IsAdminOrSelf: ['retrieve', 'list', 'update', 'partial_update', ],
        IsAuthenticated: [],
        AllowAny: ['create']
    }
