from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response

from . import models, serializers

from ...libs import views as common_views


class UserProfileViewSet(viewsets.ModelViewSet):

    queryset = models.UserProfile.objects.all()
    serializer_class = serializers.UserProfileSerializer

    permission_classes = (common_views.ActionBasedPermission,)

    action_permissions = {
        IsAdminUser: ['destroy'],
        IsAuthenticated: ['create', 'update', 'partial_update'],
        AllowAny: [ 'retrieve', 'list']
    }
