from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny

from django_filters.rest_framework import DjangoFilterBackend

from . import models, serializers, filters

from ...libs import views as common_views, permissions as common_permissions


class CommentViewSet(viewsets.ModelViewSet):

    queryset = models.Comment.objects.all()
    serializer_class = serializers.CommentSerializer
    permission_classes = (common_views.ActionBasedPermission,)
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.ContentTypeFilter

    action_permissions = {
        IsAdminUser: [],
        common_permissions.IsAdminOrSelf: [],
        IsAuthenticated: ['create', 'update', 'partial_update', 'destroy'],
        AllowAny: [ 'retrieve', 'list']
    }