import datetime
import glob
import os
import re
import subprocess

from django.conf import settings
from django.core.files.storage import FileSystemStorage

from asgiref.sync import async_to_sync

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from channels.layers import get_channel_layer

from . import serializers


@api_view(['POST'])
@permission_classes([AllowAny])
def slicer_estimation(request):

    channel_group_name = request.GET.get('channel_group_name', None)

    if channel_group_name is None:
        return Response(data={'message': 'channel group name in query params not set'},status=400)

    serializer = serializers.PrintOrderUnitSlicerEstimationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    serializer_data_copy = serializer.data

    # ************************************ #
    # *** STL and config.ini filepaths *** #
    # ************************************ #

    config_dir = os.path.join(settings.BASE_DIR, 'data', 'prusa-slicer')
    config_path = os.path.join(config_dir, 'config.ini')
    upload_dir = os.path.join('./tmp') # ! Watch out for dir owner and permissions - not working for /tmp

    in_memory_file_obj = request.FILES["file"]

    upload_filename = FileSystemStorage(location=upload_dir).save(in_memory_file_obj.name, in_memory_file_obj)
    upload_filename_without_suffix = os.path.splitext(upload_filename)[0]
    upload_path = os.path.join(upload_dir, upload_filename)

    # ********************************************** #
    # *** print order item attributes extracting *** #
    # ********************************************** #

    filament_cost = ('--filament-cost', serializer_data_copy['spool']['material'].get('filament_cost'))
    filament_density = ('--filament-density', serializer_data_copy['spool']['material'].get('filament_density'))
    extrusion_multiplier = ('--extrusion-multiplier', serializer_data_copy['spool']['material'].get('extrusion_multiplier'))
    filament_deretract_speed = ('--filament-deretract-speed', serializer_data_copy['spool']['material'].get('extrusion_multiplier'))
    filament_max_volumetric_speed = ('--filament-max-volumetric-speed', serializer_data_copy['spool']['material'].get('extrusion_multiplier'))
    filament_retract_length = ('--filament-retract-length', serializer_data_copy['spool']['material'].get('extrusion_multiplier'))
    filament_retract_lift = ('--filament-retract-lift', serializer_data_copy['spool']['material'].get('extrusion_multiplier'))
    fill_density = ('--fill-density', str(serializer_data_copy['infill']['percentage'] * 100) + '%')

    model_rotation_raw = serializer_data_copy.get('model_rotation')
    if model_rotation_raw is None:
        if os.path.isfile(upload_path):
            os.remove(upload_path)
            
        return Response(data={'message': 'Model rotation is not set'}, status=400)
    
    model_rotation_split = model_rotation_raw.split(',')
    if len(model_rotation_split) != 3:
        if os.path.isfile(upload_path):
            os.remove(upload_path)
            
        return Response(data={'message': 'Rotation string split does not have 3 values'}, status=400)
    
    try:
        rotation_x = ('--rotate-x', float(model_rotation_split[0]))
        rotation_y = ('--rotate-y', float(model_rotation_split[1]))
        rotation_z = ('--rotate', float(model_rotation_split[2]))

    except ValueError:

        if os.path.isfile(upload_path):
            os.remove(upload_path)

        return Response(data={'message': 'Couldnt parse rotation values to floats. Raw value = {}'.format(model_rotation_raw)}, status=400)

    flag_commands = [filament_cost, 
             filament_density, 
             extrusion_multiplier, 
             filament_deretract_speed, 
             filament_max_volumetric_speed,
             filament_retract_length,
             filament_retract_lift,
             fill_density,
             rotation_x, 
             rotation_y, 
             rotation_z]

    slicer_command = 'prusa-slicer --load {} --slice "{}"'.format(config_path, upload_path)
    for flag_command in flag_commands:
        if flag_command[1]:
            slicer_command += " {} {}".format(flag_command[0], flag_command[1])

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(channel_group_name, {
        "type": "slicer.estimation",
        "prusa_slicer_bash_command": slicer_command,
        "3d_model_filepath": upload_path
    })

    return Response(status=200)


    try:
        complete_process = subprocess.run(slicer_command, shell=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
        
        if complete_process.returncode == 1:
        
            error_message = 'Error occurred in subprocess command'

            output_lines = str(complete_process.stdout).split('\\n')
            for output_line in output_lines:
                if output_line.startswith('error'):
                    output_line_split = output_line.split(': ', 1)

                    if len(output_line) > 1:
                        error_message = output_line_split[1]
            
            if os.path.isfile(upload_path):
                os.remove(upload_path)

            return Response(data={'message': error_message}, status=400)
        
    except subprocess.CalledProcessError as e:
        if os.path.isfile(upload_path):
            os.remove(upload_path)

        return Response(data={'message': e}, status=400)
    
    # ***************************************** #
    # *** .gcode file estimation extraction *** #
    # ***************************************** #

    gcode_paths = glob.glob("{}/{}*gcode".format(os.path.join(upload_dir), upload_filename_without_suffix))

    if not gcode_paths:
        if os.path.isfile(upload_path):
            os.remove(upload_path)

        return Response(data={'message': '.gcode files not found in directory'}, status=400)
    if len(gcode_paths) > 1:
        if os.path.isfile(upload_path):
            os.remove(upload_path)

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

    # ************************* #
    # *** Creating response *** #
    # ************************* #

    serializer_data_copy['estimated_price'] = estimated_price
    serializer_data_copy['estimated_time'] = estimated_duration

    if os.path.isfile(upload_path):
        os.remove(upload_path)
    if os.path.isfile(gcode_path):
        os.remove(gcode_path)

    return Response(data=serializer_data_copy, status=200)