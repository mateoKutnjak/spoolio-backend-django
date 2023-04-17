from django.core.exceptions import ObjectDoesNotExist

from rest_framework import filters as drf_filters, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend

from . import models, serializers, filters

from ...libs import views as common_views, permissions as common_permissions


class CommentViewSet(viewsets.ModelViewSet, common_permissions.IsAdminOrObjectOwnerPermissionMixin):

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
        common_permissions.IsAdminOrSelf: ['update', 'partial_update', 'destroy'],
        IsAuthenticated: ['create'],
        AllowAny: [ 'retrieve', 'list']
    }

    def get_object_owner(self, obj):
        return obj.user


class LikeViewSet(viewsets.ModelViewSet, common_permissions.IsAdminOrObjectOwnerPermissionMixin):

    queryset = models.Like.objects.all()
    serializer_class = serializers.LikeSerializer
    permission_classes = (common_views.ActionBasedPermission,)
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.LikeContentTypeFilter

    action_permissions = {
        IsAdminUser: [],
        common_permissions.IsAdminOrSelf: ['update', 'partial_update', 'destroy'],
        IsAuthenticated: ['create'],
        AllowAny: [ 'retrieve', 'list']
    }

    def get_object_owner(self, obj):
        return obj.user

    @action(detail=False, methods=['post'], permission_classes=[common_permissions.IsAdminOrSelf])
    def toggle(self, request, *args, **kwargs):
        
        try:

            # * If object exists, lets delete it
            # * (We cannot propagate to destroy method because we lack pk)

            # * self.filter_queryset filters by content_type and object_id
            # * so we add additional filtering by request.user
            instance = self.filter_queryset(self.get_queryset()).filter(user=self.request.user).get()
            self.perform_destroy(instance)
            return Response(status=204)

        except ObjectDoesNotExist:

            # * Else lets propagate to create method

            return self.create(request, args, kwargs)


class RatingViewSet(viewsets.ModelViewSet, common_permissions.IsAdminOrObjectOwnerPermissionMixin):

    queryset = models.Rating.objects.all()
    serializer_class = serializers.RatingSerializer
    permission_classes = (common_views.ActionBasedPermission,)
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend, drf_filters.OrderingFilter)
    filterset_class = filters.RatingContentTypeFilter
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    action_permissions = {
        IsAdminUser: [],
        common_permissions.IsAdminOrSelf: ['update', 'partial_update', 'destroy'],
        IsAuthenticated: ['create'],
        AllowAny: [ 'retrieve', 'list']
    }

    def get_object_owner(self, obj):
        return obj.user


class ShippingAddressViewSet(viewsets.ModelViewSet):

    queryset = models.ShippingAddress.objects.all()
    serializer_class = serializers.ShippingAddressSerializer
    permission_classes = (common_views.ActionBasedPermission,)
    pagination_class = LimitOffsetPagination

    action_permissions = {
        IsAdminUser: ['update', 'partial_update', 'destroy'],
        common_permissions.IsAdminOrSelf: [],
        IsAuthenticated: ['create', 'retrieve', 'list'],
        AllowAny: []
    }


class BillingAddressViewSet(viewsets.ModelViewSet):

    queryset = models.BillingAddress.objects.all()
    serializer_class = serializers.BillingAddressSerializer
    permission_classes = (common_views.ActionBasedPermission,)
    pagination_class = LimitOffsetPagination

    action_permissions = {
        IsAdminUser: ['update', 'partial_update', 'destroy',],
        common_permissions.IsAdminOrSelf: [],
        IsAuthenticated: ['create', 'retrieve', 'list',],
        AllowAny: []
    }


class AttachmentFileViewSet(viewsets.ModelViewSet, common_permissions.IsAdminOrObjectOwnerPermissionMixin):

    queryset = models.AttachmentFile.objects.all()
    serializer_class = serializers.AttachmentFileSerializer
    permission_classes = (common_views.ActionBasedPermission,)
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.AttachmentFileContentTypeFilter

    action_permissions = {
        IsAdminUser: ['destroy'],
        common_permissions.IsAdminOrSelf: ['retrieve', 'list', 'update', 'partial_update', ],
        IsAuthenticated: [],
        AllowAny: ['create',]
    }

    def get_object_owner(self, obj):
        return obj.user


class AttachmentImageViewSet(viewsets.ModelViewSet, common_permissions.IsAdminOrObjectOwnerPermissionMixin):

    queryset = models.AttachmentImage.objects.all()
    serializer_class = serializers.AttachmentImageSerializer
    permission_classes = (common_views.ActionBasedPermission,)
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.AttachmentImageContentTypeFilter

    action_permissions = {
        IsAdminUser: ['destroy'],
        common_permissions.IsAdminOrSelf: ['retrieve', 'list', 'update', 'partial_update', ],
        IsAuthenticated: [],
        AllowAny: ['create',]
    }

    def get_object_owner(self, obj):
        return obj.user


class ShippingMethodViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = models.ShippingMethod.objects.all()
    serializer_class = serializers.ShippingMethodSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['available', ]