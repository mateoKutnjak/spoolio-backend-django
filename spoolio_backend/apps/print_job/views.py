from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend

from . import models, serializers

from ...libs import views as common_views


class PrintingJobViewSet(viewsets.ModelViewSet, viewsets.mixins.UpdateModelMixin):

    queryset = models.PrintingJob.objects.all()
    serializer_class = serializers.PrintingJobSerializer
    permission_classes = (common_views.ActionBasedPermission,)
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['printer']

    action_permissions = {
        IsAdminUser: ['create', 'update', 'partial_update', 'retrieve', 'list', 'destroy'],
        IsAuthenticated: [],
        AllowAny: ['clear_checkout']
    }

    @action(methods=['POST'], detail=False)
    def clear_checkout(self, request):
        job_ids = request.data['job_ids']
        jobs_q = self.queryset.filter(pk__in=job_ids)
        del_jobs = len(jobs_q)
        jobs_q.delete()

        return Response(del_jobs)