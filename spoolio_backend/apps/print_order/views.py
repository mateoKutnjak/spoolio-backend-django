from rest_framework import viewsets, filters
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny

from . import models, serializers

from ...libs import views as common_views


class PrintOrderViewSet(viewsets.ModelViewSet):

    queryset = models.PrintOrder.objects.all()
    serializer_class = serializers.PrintOrderSerializer
    permission_classes = (common_views.ActionBasedPermission,)
    pagination_class = LimitOffsetPagination

    action_permissions = {
        IsAdminUser: ['retrieve', 'list', 'update', 'partial_update', 'destroy'],
        IsAuthenticated: [],
        AllowAny: [ 'create', ]
    }
