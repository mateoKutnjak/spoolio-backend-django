from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny

from django_filters.rest_framework import DjangoFilterBackend

from . import models, serializers

from ...libs import views as common_views


class PrintingJobViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = models.PrintingJob.objects.all()
    serializer_class = serializers.PrintingJobSerializer
    permission_classes = (common_views.ActionBasedPermission,)
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['printer']

    action_permissions = {
        IsAdminUser: ['create', 'update', 'partial_update', 'retrieve', 'list', 'destroy'],
        IsAuthenticated: [],
        AllowAny: []
    }