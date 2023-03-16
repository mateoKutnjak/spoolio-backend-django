from abc import ABCMeta, abstractmethod

from django.shortcuts import get_object_or_404

from rest_framework import permissions


class IsAdminOrSelf(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True
        return False
        
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        if request.user.is_staff:
            return True
        
        get_object_owner = getattr(view, "get_object_owner", None)
        if callable(get_object_owner):
            return request.user == get_object_owner(obj)
        
        return False


class IsAdminOrObjectOwnerPermissionMixin(object):

    __metaclass__ = ABCMeta

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        return obj

    @abstractmethod
    def get_object_owner(self, obj):
        raise NotImplementedError("Impelment this method in ViewSet to use IsAdminOrSelf permission")