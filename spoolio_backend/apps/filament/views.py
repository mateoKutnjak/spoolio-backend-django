from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny

from django_filters.rest_framework import DjangoFilterBackend

from . import models, serializers

from ...libs import views as common_views, permissions as common_permissions


class ColorViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = models.Color.objects.all()
    serializer_class = serializers.ColorSerializer
    permission_classes = (common_views.ActionBasedPermission,)
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['available', ]

    action_permissions = {
        IsAdminUser: ['create', 'update', 'partial_update', 'destroy'],
        common_permissions.IsAdminOrSelf: [],
        IsAuthenticated: [],
        AllowAny: [ 'retrieve', 'list' ]
    }


class MaterialViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = models.Material.objects.all()
    serializer_class = serializers.MaterialSerializer
    permission_classes = (common_views.ActionBasedPermission,)
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['available', ]

    action_permissions = {
        IsAdminUser: ['create', 'update', 'partial_update', 'destroy'],
        common_permissions.IsAdminOrSelf: [],
        IsAuthenticated: [],
        AllowAny: [ 'retrieve', 'list' ]
    }


class InfillViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = models.Infill.objects.all()
    serializer_class = serializers.InfillSerializer
    permission_classes = (common_views.ActionBasedPermission,)
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['available', ]

    action_permissions = {
        IsAdminUser: ['create', 'update', 'partial_update', 'destroy'],
        common_permissions.IsAdminOrSelf: [],
        IsAuthenticated: [],
        AllowAny: [ 'retrieve', 'list' ]
    }


class SpoolViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = models.Spool.objects.all()
    serializer_class = serializers.SpoolSerializer
    permission_classes = (common_views.ActionBasedPermission,)
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['available', ]

    action_permissions = {
        IsAdminUser: ['create', 'update', 'partial_update', 'destroy'],
        common_permissions.IsAdminOrSelf: [],
        IsAuthenticated: [],
        AllowAny: [ 'retrieve', 'list' ]
    }