from django.shortcuts import get_object_or_404

from rest_framework import viewsets, filters, mixins
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response

from . import models, serializers

from ...libs import views as common_views


class BlogViewSet(viewsets.ModelViewSet):

    queryset = models.Blog.objects.all()
    serializer_class = serializers.BlogSerializer
    permission_classes = (common_views.ActionBasedPermission,)

    action_permissions = {
        IsAdminUser: ['destroy'],
        IsAuthenticated: [],
        AllowAny: ['create', 'update', 'partial_update', 'retrieve', 'list', 'destroy']
    }

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=isinstance(request.data, list))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    def retrieve(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        item = get_object_or_404(queryset, pk=self.kwargs.get('pk'))
        serializer = self.get_serializer(item)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)