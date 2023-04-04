import datetime
import glob
import os
import re
import subprocess

from django.conf import settings
from django.core.files.storage import FileSystemStorage

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from . import serializers


@api_view(['POST'])
@permission_classes([AllowAny])
def slicer_estimation(request):

    serializer = serializers.PrintOrderUnitSlicerEstimationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    serializer_data_copy = serializer.data

    config_dir = os.path.join(settings.BASE_DIR, 'data', 'prusa-slicer')
    config_path = os.path.join(config_dir, 'config.ini')
    upload_dir = os.path.join('/home/mateo/Downloads/') # ! Watch out for dir owner and permissions - not working for /tmp

    in_memory_file_obj = request.FILES["file"]

    upload_filename = FileSystemStorage(location=upload_dir).save(in_memory_file_obj.name, in_memory_file_obj)
    upload_filename_without_suffix = os.path.splitext(upload_filename)[0]
    upload_path = os.path.join(upload_dir, upload_filename)

    r = subprocess.check_output('prusa-slicer --load {} --slice {}'.format(config_path, upload_path), shell=True)
    
    gcode_paths = glob.glob("{}/{}*gcode".format(os.path.join(upload_dir), upload_filename_without_suffix))

    if not gcode_paths:
        return Response(data={'message': '.gcode files not found in directory'}, status=400)
    if len(gcode_paths) > 1:
        return Response(data={'message': 'Duplicated .gcode files'}, status=400)
    
    gcode_path = gcode_paths[0]
    gcode_filename = os.path.basename(gcode_path)
    gcode_filename_without_suffix = os.path.splitext(gcode_filename)[0]

    estimated_duration_raw = gcode_filename_without_suffix.split('_')[-3]
    estimated_price_raw = gcode_filename_without_suffix.split('_')[-1]

    pattern = re.compile(r"(\d+d)?(\d+h)?(\d+m)?")
    estimated_duration_split = pattern.search(estimated_duration_raw).groups()
    if len(estimated_duration_split) != 3:

        if os.path.isfile(upload_path):
            os.remove(upload_path)
        if os.path.isfile(gcode_path):
            os.remove(gcode_path)

        return Response(data={'message': 'Split DHM format invalid length. Expected 3, got {}'.format(len(estimated_duration_split))}, status=400)

    estimated_duration_days_raw = estimated_duration_split[0].replace("d", "") if estimated_duration_split[0] is not None else '0'
    estimated_duration_hours_raw = estimated_duration_split[1].replace("h", "") if estimated_duration_split[1] is not None else '0'
    estimated_duration_minutes_raw = estimated_duration_split[2].replace("m", "") if estimated_duration_split[2] is not None else '0'

    try:
        estimated_duration = datetime.timedelta(
            days=int(estimated_duration_days_raw),
            hours=int(estimated_duration_hours_raw),
            minutes=int(estimated_duration_minutes_raw),
        ).seconds
    except ValueError:

        if os.path.isfile(upload_path):
            os.remove(upload_path)
        if os.path.isfile(gcode_path):
            os.remove(gcode_path)

        return Response(data={'message': 'Error while parsing duration DHM format: raw value = {}'.format(estimated_duration_raw)}, status=400)
    
    estimated_price = float(estimated_price_raw)

    serializer_data_copy['estimated_price'] = estimated_price
    serializer_data_copy['estimated_time'] = estimated_duration

    if os.path.isfile(upload_path):
        os.remove(upload_path)
    if os.path.isfile(gcode_path):
        os.remove(gcode_path)

    return Response(data=serializer_data_copy, status=200)