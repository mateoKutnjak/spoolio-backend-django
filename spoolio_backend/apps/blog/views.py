from django.shortcuts import get_object_or_404

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


class SubcategoryViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = models.Subcategory.objects.all()
    serializer_class = serializers.SubcategorySerializer
    permission_classes = (common_views.ActionBasedPermission,)

    action_permissions = {
        IsAdminUser: ['create', 'update', 'partial_update', 'destroy'],
        common_permissions.IsAdminOrSelf: [],
        IsAuthenticated: [], 
        AllowAny: ['retrieve', 'list']
    }


class TagViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer
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
    filter_class = filters.BlogCategoryFilter
    search_fields = ('title', 'subtitle', 'author__email')
    filterset_fields = ('category', )

    action_permissions = {
        IsAdminUser: ['create'],
        common_permissions.IsAdminOrSelf: ['update', 'partial_update', 'destroy'],
        IsAuthenticated: [], 
        AllowAny: ['retrieve', 'list']
    }

    def get_object_owner(self, obj):
        return obj.author