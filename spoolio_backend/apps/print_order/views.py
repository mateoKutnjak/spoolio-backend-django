from rest_framework import viewsets
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

    action_permissions = {
        IsAdminUser: ['retrieve', 'list', 'update', 'partial_update', 'destroy'],
        common_permissions.IsAdminOrSelf: [],
        IsAuthenticated: [],
        AllowAny: [ 'create' ]
    }

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)


class PrintOrderUnitViewSet(viewsets.ModelViewSet):

    queryset = models.OrderUnit.objects.all()
    serializer_class = serializers.PrintOrderUnitSerializer
    permission_classes = (common_views.ActionBasedPermission,)
    pagination_class = LimitOffsetPagination

    action_permissions = {
        IsAdminUser: ['retrieve', 'list', 'update', 'partial_update', 'destroy'],
        common_permissions.IsAdminOrSelf: [],
        IsAuthenticated: [],
        AllowAny: ['create']
    }

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)