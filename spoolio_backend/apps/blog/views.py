from rest_framework import viewsets, filters
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny

from . import models, serializers

from ...libs import views as common_views


class BlogViewSet(viewsets.ModelViewSet):

    queryset = models.Blog.objects.all()
    serializer_class = serializers.BlogSerializer
    permission_classes = (common_views.ActionBasedPermission,)
    pagination_class = LimitOffsetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', ]

    action_permissions = {
        IsAdminUser: ['create', 'update', 'partial_update', 'destroy'],
        IsAuthenticated: [],
        AllowAny: [ 'retrieve', 'list']
    }