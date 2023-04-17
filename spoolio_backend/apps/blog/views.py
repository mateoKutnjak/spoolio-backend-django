from django.shortcuts import get_object_or_404

from rest_framework import viewsets, filters
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny

from django_filters.rest_framework import DjangoFilterBackend

from . import models, serializers

from ...libs import views as common_views, permissions as common_permissions


class BlogViewSet(viewsets.ModelViewSet, common_permissions.IsAdminOrObjectOwnerPermissionMixin):

    queryset = models.Blog.objects.all()
    serializer_class = serializers.BlogSerializer
    permission_classes = (common_views.ActionBasedPermission,)
    pagination_class = LimitOffsetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', ]

    action_permissions = {
        IsAdminUser: ['create'],
        common_permissions.IsAdminOrSelf: ['update', 'partial_update', 'destroy'],
        IsAuthenticated: [], 
        AllowAny: ['retrieve', 'list']
    }

    def get_object_owner(self, obj):
        return obj.author