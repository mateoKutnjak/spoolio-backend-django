from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny

from . import models, serializers

from ...libs import views as common_views


class PrinterTypeViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = models.PrinterType.objects.all()
    serializer_class = serializers.PrinterTypeSerializer
    permission_classes = (common_views.ActionBasedPermission,)
    pagination_class = LimitOffsetPagination

    action_permissions = {
        IsAdminUser: ['create', 'update', 'partial_update', 'retrieve', 'list', 'destroy'],
        IsAuthenticated: [],
        AllowAny: []
    }


class PrinterViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = models.Printer.objects.all()
    serializer_class = serializers.PrinterSerializer
    permission_classes = (common_views.ActionBasedPermission,)
    pagination_class = LimitOffsetPagination

    action_permissions = {
        IsAdminUser: ['create', 'update', 'partial_update', 'retrieve', 'list', 'destroy'],
        IsAuthenticated: [],
        AllowAny: []
    }


class PrintingMethodViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = models.PrintingMethod.objects.all()
    serializer_class = serializers.PrintingMethodSerializer
    permission_classes = (common_views.ActionBasedPermission,)

    action_permissions = {
        IsAdminUser: ['create', 'update', 'partial_update', 'destroy'],
        IsAuthenticated: [],
        AllowAny: ['retrieve', 'list']
    }