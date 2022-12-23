from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response

from . import models, serializers

from ...libs import views as common_views, permissions as common_permissions


class UserProfileViewSet(viewsets.ModelViewSet):

    queryset = models.UserProfile.objects.all()
    serializer_class = serializers.UserProfileSerializer

    permission_classes = (common_views.ActionBasedPermission,)

    action_permissions = {
        IsAdminUser: ['destroy'],
        common_permissions.IsAdminOrSelf: [],
        IsAuthenticated: ['create', 'update', 'partial_update'],
        AllowAny: [ 'retrieve', 'list']
    }

    def update(self, request, *args, **kwargs):
        import pdb
        pdb.set_trace()

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)