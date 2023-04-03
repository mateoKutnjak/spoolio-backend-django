from django.contrib.auth.models import AnonymousUser

from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend

from . import models, serializers

from .. filament import models as filament_models

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
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny], url_path='slicer-estimate', serializer_class=serializers.PrintOrderUnitSlicerEstimationSerializer)
    def slicer_estimate(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer_data_copy = serializer.data

        # TODO perform slicer call to get time and price estimation
        # TODO fill estimated_price and estimated_time like this:
        # TODO -> serializer_data_copy['estimated_price'] = '9000'

        return Response(data=serializer_data_copy, status=200)