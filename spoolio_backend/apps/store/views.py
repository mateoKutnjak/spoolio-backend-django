from rest_framework import viewsets, filters as drf_filters
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny

from django_filters.rest_framework import DjangoFilterBackend

from . import models, serializers, filters

from ...libs import views as common_views, permissions as common_permissions



class ProductCategoryViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = models.ProductCategory.objects.all()
    serializer_class = serializers.ProductCategorySerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [drf_filters.SearchFilter]
    search_fields = ['name', ]


class ProductSubcategoryViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = models.ProductSubcategory.objects.all()
    serializer_class = serializers.ProductSubcategorySerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [drf_filters.SearchFilter]
    search_fields = ['name', ]


class ProductViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = models.Product.objects.all()
    serializer_class = serializers.ProductSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [drf_filters.SearchFilter]
    search_fields = ['title', ]


class ProductVariationViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = models.ProductVariation.objects.all()
    serializer_class = serializers.ProductVariationSerializer


class ProductVariationOptionViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = models.ProductVariationOption.objects.all()
    serializer_class = serializers.ProductVariationOptionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product', ]


class ProductVariationOptionCombinationViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = models.ProductVariationOptionCombination.objects.all()
    serializer_class = serializers.ProductVariationOptionCombinationSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.ProductVariationOptionCombinationFilter