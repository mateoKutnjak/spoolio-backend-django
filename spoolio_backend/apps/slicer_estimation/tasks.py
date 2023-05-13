import datetime
import glob
import logging
import os
import re
import subprocess

from asgiref.sync import async_to_sync

from celery import shared_task
from channels.layers import get_channel_layer

from ..print_job import utils as print_job_utils


logger = logging.getLogger(__name__)


@shared_task()
def task_execute(job_params):

    def cleanFiles():
        try:
            if os.path.isfile(model_filepath):
                os.remove(model_filepath)
        except NameError:
            pass # * Variable is not defined

        try:
            if os.path.isfile(gcode_path):
                os.remove(gcode_path)
        except NameError:
            pass # * Variable is not defined

    # ************************************************ #
    # *** Check websocket communication parameters *** #
    # ************************************************ #

    channel_group_name = job_params.get('meta', {}).get('django_channels', {}).get('channel_group_name', None)

    if not channel_group_name:
        logger.error('Celery task stopped. Parameter "channel_group_name" missing')
        return

    # ********************************* #
    # *** Check required parameters *** #
    # ********************************* #

    model_filepath = job_params.get('task', {}).get('meta', {}).get('model_filepath')
    config_filepath = job_params.get('task', {}).get('meta', {}).get('config_filepath')

    required_parameters = {
        '--slice': model_filepath,
        '--config': config_filepath
    }

    for required_parameter in required_parameters:
        if not required_parameter:
            onError('Celery task stopped. Parameter {} missing', channel_group_name=channel_group_name)
            return

    # ****************************** #
    # *** Check other parameters *** #
    # ****************************** #

    print_order_unit = job_params.get('task', {}).get('data', {}).get('print_order_unit', {})

    other_units = job_params.get('task', {}).get('data', {}).get('other_units', [])

    quantity = print_order_unit.get('quantity')
    material = print_order_unit.get('spool', {}).get('material', {})
    fill_density = print_order_unit.get('infill', {}).get('percentage')
    model_rotation_raw = print_order_unit.get('model_rotation')

    filament_cost = material.get('filament_cost')
    filament_density = material.get('filament_density')
    extrusion_multiplier = material.get('extrusion_multiplier')
    filament_deretract_speed = material.get('filament_deretract_speed')
    filament_max_volumetric_speed = material.get('filament_max_volumetric_speed')
    filament_retract_length = material.get('filament_retract_length')
    filament_retract_lift = material.get('filament_retract_lift')


    quantity = print_order_unit.get('quantity')
    material = print_order_unit.get('spool', {}).get('material')
    
    if quantity is None or not material:
        onError('Quantity (={}) or material (={}) is not set'.format(quantity, material), channel_group_name=channel_group_name)
        return

    # * Parsing model rotation

    rotation_x, rotation_y, rotation_z, error_message = parse_model_rotation(model_rotation_raw)

    if error_message:
        onError(error_message, channel_group_name=channel_group_name)
        return
    
    # * Checking existance of prusa-slicer command flags

    params = {
        '--filament-cost': filament_cost,
        '--filament-density': filament_density,
        '--extrusion-multiplier': extrusion_multiplier,
        '--filament-deretract-speed': filament_deretract_speed,
        '--filament-max-volumetric-speed': filament_max_volumetric_speed,
        '--filament-retract-length': filament_retract_length,
        '--filament-retract-lift': filament_retract_lift,
        '--fill-density': str(int(fill_density * 100)) + "%" if fill_density else None,
        '--rotate-x': rotation_x,
        '--rotate-y': rotation_y,
        '--rotate': rotation_z,
    }

    # ********************************** #
    # *** Build prusa-slicer command *** #
    # ********************************** #

    slicer_command = 'prusa-slicer --load {} --slice "{}"'.format(config_filepath, model_filepath)
    for flag, value in params.items():
        if value is not None:
            slicer_command += " {} {}".format(flag, value)

    print(slicer_command)

    # ************************** #
    # *** Run slicer command *** #
    # ************************** #

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
            
            onError(error_message, channel_group_name=channel_group_name)
            cleanFiles()
            return
        
    except subprocess.CalledProcessError as e:
        onError(str(e), channel_group_name=channel_group_name)
        cleanFiles()
        return
    
    # ************************************ #
    # *** .GCODE ESTIMATION EXTRACTION *** #
    # ************************************ #

    model_filepath_without_suffix = os.path.splitext(model_filepath)[0]
    gcode_paths = glob.glob("{}*gcode".format(model_filepath_without_suffix))

    if not gcode_paths:
        onError('.gcode files not found in directory', channel_group_name=channel_group_name)
        cleanFiles()
        return

    if len(gcode_paths) > 1:
        onError('Duplicated .gcode files', channel_group_name=channel_group_name)
        cleanFiles()
        return

    gcode_path = gcode_paths[0]
    gcode_filename = os.path.basename(gcode_path)
    gcode_filename_without_suffix = os.path.splitext(gcode_filename)[0]

    estimated_duration_raw = gcode_filename_without_suffix.split('_')[-3]
    estimated_price_raw = gcode_filename_without_suffix.split('_')[-1]

    cleanFiles()

    pattern = re.compile(r"(\d+d)?(\d+h)?(\d+m)?")
    estimated_duration_split = pattern.search(estimated_duration_raw).groups()
    if len(estimated_duration_split) != 3:

        onError('Split DHM format invalid length. Expected 3, got {}'.format(len(estimated_duration_split)), channel_group_name=channel_group_name)
        cleanFiles()
        return

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

        onError('Error while parsing duration DHM format: raw value = {}'.format(estimated_duration_raw), channel_group_name=channel_group_name)
        cleanFiles()
        return

    estimated_price = float(estimated_price_raw)

    units = [print_job_utils.PrintOrderUnitPlaceholder(
        quantity=u['quantity'], 
        material_id=u['material']['id'], 
        estimated_time=u['estimated_time']) for u in other_units]
    units.append(print_job_utils.PrintOrderUnitPlaceholder(quantity=quantity, estimated_time=estimated_duration, material_id=material['id']))

    estimated_ending_time = print_job_utils.generate_print_jobs(units, fake=True)

    onSuccess(estimated_price, estimated_duration, estimated_ending_time, channel_group_name=channel_group_name)

def parse_model_rotation(model_rotation_raw: str):
    if model_rotation_raw is None:
        return None, None, None, 'Model rotation string is None'
    
    model_rotation_split = model_rotation_raw.split(',')
    if len(model_rotation_split) != 3:
        return None, None, None, 'Model rotation string split by delimiter "," does not give 3 values'
    
    try:
        rotation_x = float(model_rotation_split[0])
        rotation_y = float(model_rotation_split[1])
        rotation_z = float(model_rotation_split[2])
                      
    except ValueError:
        return None, None, None, "Some of the values in model rotation cannot be parsed as float"
    
    return rotation_x, rotation_y, rotation_z, None

def onError(error_message, channel_group_name):
    logger.error(error_message)
    
    if channel_group_name:
        channel_layer = get_channel_layer()

        async_to_sync(channel_layer.group_send)(channel_group_name, {
            "type": "slicer.estimation.error",
            "payload": {
                "type": 'error',
                "message": error_message
            }
        })

def onSuccess(estimated_price, estimated_time, estimated_ending_time, channel_group_name):
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(channel_group_name, {
        "type": "slicer.estimation.success",
        "payload": {
            "type": 'success',
            "data": {
                "estimated_time": estimated_time, 
                "estimated_price": estimated_price,
                "estimated_ending_time": estimated_ending_time.isoformat(),
            }
        }
    })