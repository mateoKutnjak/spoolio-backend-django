from rest_framework import viewsets, filters as drf_filters
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny

from django_filters.rest_framework import DjangoFilterBackend

from . import models, serializers, filters

from ...libs import views as common_views, permissions as common_permissions



class ProductCategoryViewSet(viewsets.ModelViewSet):

    queryset = models.ProductCategory.objects.all()
    serializer_class = serializers.ProductCategorySerializer
    permission_classes = (common_views.ActionBasedPermission,)
    pagination_class = LimitOffsetPagination
    filter_backends = [drf_filters.SearchFilter]
    search_fields = ['name', ]

    action_permissions = {
        IsAdminUser: ['create', 'update', 'partial_update', 'destroy'],
        common_permissions.IsAdminOrSelf: [],
        IsAuthenticated: [],
        AllowAny: [ 'retrieve', 'list']
    }


class ProductSubcategoryViewSet(viewsets.ModelViewSet):

    queryset = models.ProductSubcategory.objects.all()
    serializer_class = serializers.ProductSubcategorySerializer
    permission_classes = (common_views.ActionBasedPermission,)
    pagination_class = LimitOffsetPagination
    filter_backends = [drf_filters.SearchFilter]
    search_fields = ['name', ]

    action_permissions = {
        IsAdminUser: ['create', 'update', 'partial_update', 'destroy'],
        common_permissions.IsAdminOrSelf: [],
        IsAuthenticated: [],
        AllowAny: [ 'retrieve', 'list']
    }


class ProductViewSet(viewsets.ModelViewSet):

    queryset = models.Product.objects.all()
    serializer_class = serializers.ProductSerializer
    permission_classes = (common_views.ActionBasedPermission,)
    pagination_class = LimitOffsetPagination
    filter_backends = [drf_filters.SearchFilter]
    search_fields = ['title', ]

    action_permissions = {
        IsAdminUser: ['create', 'update', 'partial_update', 'destroy'],
        common_permissions.IsAdminOrSelf: [],
        IsAuthenticated: [],
        AllowAny: [ 'retrieve', 'list']
    }


class ProductVariationViewSet(viewsets.ModelViewSet):

    queryset = models.ProductVariation.objects.all()
    serializer_class = serializers.ProductVariationSerializer
    permission_classes = (common_views.ActionBasedPermission,)

    action_permissions = {
        IsAdminUser: ['create', 'update', 'partial_update', 'destroy'],
        common_permissions.IsAdminOrSelf: [],
        IsAuthenticated: [],
        AllowAny: [ 'retrieve', 'list']
    }


class ProductVariationOptionViewSet(viewsets.ModelViewSet):

    queryset = models.ProductVariationOption.objects.all()
    serializer_class = serializers.ProductVariationOptionSerializer
    permission_classes = (common_views.ActionBasedPermission,)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product', ]
    
    action_permissions = {
        IsAdminUser: ['create', 'update', 'partial_update', 'destroy'],
        common_permissions.IsAdminOrSelf: [],
        IsAuthenticated: [],
        AllowAny: [ 'retrieve', 'list']
    }


class ProductVariationOptionCombinationViewSet(viewsets.ModelViewSet):

    queryset = models.ProductVariationOptionCombination.objects.all()
    serializer_class = serializers.ProductVariationOptionCombinationSerializer
    permission_classes = (common_views.ActionBasedPermission,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.ProductVariationOptionCombinationFilter

    action_permissions = {
        IsAdminUser: ['create', 'update', 'partial_update', 'destroy'],
        common_permissions.IsAdminOrSelf: [],
        IsAuthenticated: [],
        AllowAny: [ 'retrieve', 'list']
    }