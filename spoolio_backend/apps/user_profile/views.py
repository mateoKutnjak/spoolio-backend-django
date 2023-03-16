from django.contrib.auth.models import AnonymousUser

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny

from . import models, serializers

from ...libs import views as common_views, permissions as common_permissions


class UserProfileViewSet(viewsets.ModelViewSet, common_permissions.IsAdminOrObjectOwnerPermissionMixin):

    queryset = models.UserProfile.objects.all()
    serializer_class = serializers.UserProfileSerializer
    permission_classes = (common_views.ActionBasedPermission,)

    action_permissions = {
        IsAdminUser: ['update', 'retrieve', 'list', 'destroy'],
        common_permissions.IsAdminOrSelf: ['partial_update'],
        IsAuthenticated: ['create',],
        AllowAny: []
    }

    def get_object_owner(self, obj):
        return obj.user or AnonymousUser