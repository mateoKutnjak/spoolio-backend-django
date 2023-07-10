from rest_framework import viewsets, filters as drf_filters
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny

from django_filters.rest_framework import DjangoFilterBackend

from . import filters, models, serializers

from ...libs import views as common_views, permissions as common_permissions


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer
    permission_classes = (common_views.ActionBasedPermission,)

    action_permissions = {
        IsAdminUser: ['create', 'update', 'partial_update', 'destroy'],
        common_permissions.IsAdminOrSelf: [],
        IsAuthenticated: [], 
        AllowAny: ['retrieve', 'list']
    }


class BlogViewSet(viewsets.ModelViewSet, common_permissions.IsAdminOrObjectOwnerPermissionMixin):

    queryset = models.Blog.objects.all()
    serializer_class = serializers.BlogSerializer
    permission_classes = (common_views.ActionBasedPermission,)
    pagination_class = LimitOffsetPagination

    filter_backends = [drf_filters.SearchFilter, DjangoFilterBackend]
    filter_class = filters.BlogFilter
    search_fields = ('title', 'subtitle')
    filterset_fields = ('category')

    action_permissions = {
        IsAdminUser: ['create', 'update', 'partial_update', 'destroy'],
        common_permissions.IsAdminOrSelf: [],
        IsAuthenticated: [], 
        AllowAny: ['retrieve', 'list']
    }