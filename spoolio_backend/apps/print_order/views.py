from django.contrib.auth.models import AnonymousUser

from rest_framework import filters, viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend

from . import models, serializers

from ...libs import views as common_views, permissions as common_permissions


class PrintOrderViewSet(viewsets.ModelViewSet, common_permissions.IsAdminOrObjectOwnerPermissionMixin):

    queryset = models.PrintOrder.objects.all()
    serializer_class = serializers.PrintOrderSerializer
    permission_classes = (common_views.ActionBasedPermission,)
    pagination_class = LimitOffsetPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    action_permissions = {
        IsAdminUser: ['update', 'destroy'],
        common_permissions.IsAdminOrSelf: ['retrieve', 'list', 'partial_update', ],
        IsAuthenticated: [],
        AllowAny: ['create',]
    }

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset()).exclude(status__in=[models.PrintOrder.STATUS_AWAITING_PAYMENT])

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        # * As this method filters only order which belong to request.user,
        # * nobody else can perform any changes on this object
        return models.PrintOrder.objects.filter(user_profile__user=self.request.user)

    def get_object_owner(self, obj):
        if obj.user_profile:
            return obj.user_profile.user or AnonymousUser
        return AnonymousUser


class PrintOrderUnitViewSet(viewsets.ModelViewSet, common_permissions.IsAdminOrObjectOwnerPermissionMixin):

    queryset = models.OrderUnit.objects.all()
    serializer_class = serializers.PrintOrderUnitSerializer
    permission_classes = (common_views.ActionBasedPermission,)
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['order']

    action_permissions = {
        IsAdminUser: ['update', 'partial_update', 'destroy'],
        common_permissions.IsAdminOrSelf: ['retrieve', 'list', ],
        IsAuthenticated: [],
        AllowAny: ['create']
    }

    def get_queryset(self):
        # * As this method filters only order which belong to request.user,
        # * nobody else can perform any changes on this object
        return models.OrderUnit.objects.filter(order__user_profile__user=self.request.user)

    def get_object_owner(self, obj):
        if obj.user_profile:
            return obj.user_profile.user or AnonymousUser
        return AnonymousUser
    

class PrintUnitInfillViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = models.PrintUnitInfill.objects.all()
    serializer_class = serializers.PrintUnitInfillSerializer


class PrintUnitWallViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = models.PrintUnitWall.objects.all()
    serializer_class = serializers.PrintUnitWallSerializer


class PrintUnitWallThicknessViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = models.PrintUnitWallThickness.objects.all()
    serializer_class = serializers.PrintUnitWallThicknessSerializer


class PrintUnitInfillWallCombinationViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = models.PrintUnitInfillWallCombination.objects.all()
    serializer_class = serializers.PrintUnitInfillWallCombinationSerializer