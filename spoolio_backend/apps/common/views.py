from django.core.exceptions import ObjectDoesNotExist

from rest_framework import filters as drf_filters, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend

from . import models, serializers, filters

from ...libs import views as common_views, permissions as common_permissions


class CommentViewSet(viewsets.ModelViewSet):

    queryset = models.Comment.objects.all()
    serializer_class = serializers.CommentSerializer
    permission_classes = (common_views.ActionBasedPermission,)
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend, drf_filters.OrderingFilter)
    filterset_class = filters.CommentContentTypeFilter
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    action_permissions = {
        IsAdminUser: [],
        common_permissions.IsAdminOrSelf: [],
        IsAuthenticated: ['create', 'update', 'partial_update', 'destroy'],
        AllowAny: [ 'retrieve', 'list']
    }


class LikeViewSet(viewsets.ModelViewSet):

    queryset = models.Like.objects.all()
    serializer_class = serializers.LikeSerializer
    permission_classes = (common_views.ActionBasedPermission,)
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.LikeContentTypeFilter

    action_permissions = {
        IsAdminUser: [],
        common_permissions.IsAdminOrSelf: [],
        IsAuthenticated: ['create', 'update', 'partial_update', 'destroy'],
        AllowAny: [ 'retrieve', 'list']
    }

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def toggle(self, request, *args, **kwargs):
        
        try:

            # * If object exists, lets delete it
            # * (We cannot propagate to destroy method because we lack pk)

            instance = self.filter_queryset(self.get_queryset()).get()
            self.perform_destroy(instance)
            return Response(status=204)

        except ObjectDoesNotExist:

            # * Else lets propagate to delete method

            return self.create(request, args, kwargs)


class ShippingAddressViewSet(viewsets.ModelViewSet):

    queryset = models.ShippingAddress.objects.all()
    serializer_class = serializers.ShippingAddressSerializer
    permission_classes = (common_views.ActionBasedPermission,)
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.LikeContentTypeFilter

    action_permissions = {
        IsAdminUser: [],
        common_permissions.IsAdminOrSelf: [],
        IsAuthenticated: ['create', 'update', 'partial_update', 'retrieve', 'list', 'destroy'],
        AllowAny: []
    }


class BillingAddressViewSet(viewsets.ModelViewSet):

    queryset = models.BillingAddress.objects.all()
    serializer_class = serializers.BillingAddressSerializer
    permission_classes = (common_views.ActionBasedPermission,)
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.LikeContentTypeFilter

    action_permissions = {
        IsAdminUser: [],
        common_permissions.IsAdminOrSelf: [],
        IsAuthenticated: ['create', 'update', 'partial_update', 'retrieve', 'list', 'destroy'],
        AllowAny: []
    }


class AttachmentFileViewSet(viewsets.ModelViewSet):

    queryset = models.AttachmentFile.objects.all()
    serializer_class = serializers.AttachmentFileSerializer
    permission_classes = (common_views.ActionBasedPermission,)
    pagination_class = LimitOffsetPagination

    action_permissions = {
        IsAdminUser: ['destroy'],
        common_permissions.IsAdminOrSelf: ['retrieve', 'list', 'update', 'partial_update', ],
        IsAuthenticated: [],
        AllowAny: ['create',]
    }


class AttachmentImageViewSet(viewsets.ModelViewSet):

    queryset = models.AttachmentImage.objects.all()
    serializer_class = serializers.AttachmentImageSerializer
    permission_classes = (common_views.ActionBasedPermission,)
    pagination_class = LimitOffsetPagination

    action_permissions = {
        IsAdminUser: ['destroy'],
        common_permissions.IsAdminOrSelf: ['retrieve', 'list', 'update', 'partial_update', ],
        IsAuthenticated: [],
        AllowAny: ['create',]
    }


class ShippingMethodViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = models.ShippingMethod.objects.all()
    serializer_class = serializers.ShippingMethodSerializer
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