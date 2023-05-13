import json
import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from . import serializers, tasks

from .. print_order import serializers as print_order_serializers


@api_view(['POST'])
@permission_classes([AllowAny])
def slicer_estimation(request):

    channel_group_name = request.GET.get('channel_group_name', None)

    if channel_group_name is None:
        return Response(data={'message': 'channel group name in query params not set'},status=400)

    serializer = serializers.PrintOrderUnitSlicerEstimationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    serializer_other_units = print_order_serializers.PrintOrderUnitPlaceholderSerializer(data=json.loads(request.data.get('other_units', '[]')), many=True)
    serializer_other_units.is_valid(raise_exception=False)

    # ************************************ #
    # *** STL and config.ini filepaths *** #
    # ************************************ #

    config_dir = os.path.join(settings.BASE_DIR, 'data', 'prusa-slicer')
    config_path = os.path.join(config_dir, 'config.ini')
    upload_dir = os.path.join('./tmp') # ! Watch out for dir owner and permissions - not working for /tmp

    in_memory_file_obj = request.FILES["file"]

    upload_filename = FileSystemStorage(location=upload_dir).save(in_memory_file_obj.name, in_memory_file_obj)
    upload_path = os.path.join(upload_dir, upload_filename)

    # ************************************************ #
    # *** Forward slicer estimation task to Celery *** #
    # ************************************************ #

    tasks.task_execute.delay({
        'meta': {
            'django_channels': {
                'channel_group_name': channel_group_name, 
            },
        },
        'task': {
            'data': {
                'print_order_unit': serializer.data,
                'other_units': json.loads(request.data.get('other_units', '[]'))
            },
            'meta': {
                "model_filepath": upload_path,
                'config_filepath': config_path,
            }
        }
    })

    return Response(status=200)
