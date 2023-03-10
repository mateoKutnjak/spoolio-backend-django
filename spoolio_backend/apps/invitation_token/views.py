from rest_framework import viewsets, filters as drf_filters
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny

from . import models, serializers

from ...libs import views as common_views, permissions as common_permissions


class InvitationTokenViewSet(viewsets.ModelViewSet):

    queryset = models.InvitationToken.objects.all()
    serializer_class = serializers.InvitationTokenSerializer
    permission_classes = (common_views.ActionBasedPermission,)

    action_permissions = {
        IsAdminUser: ['create', 'update', 'partial_update', 'destroy', 'retrieve', 'list'],
        common_permissions.IsAdminOrSelf: [],
        IsAuthenticated: [],
        AllowAny: []
    }