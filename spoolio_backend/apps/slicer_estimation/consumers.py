import datetime
import glob
import json
import logging
import os
import re
import subprocess
import uuid

from channels.generic.websocket import AsyncWebsocketConsumer

from .. slicer_estimation import serializers


logger = logging.getLogger(__name__)


class SlicerEstimationConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        self.channel_group_name = str(uuid.uuid4())

        await self.channel_layer.group_add(
            self.channel_group_name,
            self.channel_name
        )

        await self.accept()
        await self.send(text_data=json.dumps({
            "type": "init",
            "meta": {
                "channel_group_name": self.channel_group_name, 
            }
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.channel_group_name, self.channel_name)

    async def slicer_estimation(self, event):

        # ******************************************** #
        # *** CHECK EVENT DATA DICTIONARY VALIDITY *** #
        # ******************************************** #

        command = event.get('command')
        if not command:
            logger.error('Expected event dict with key "command". Event received = {}'.format(event))
            return
        
        model_filepath = event.get('model_filepath')
        if not model_filepath:
            logger.error('Expected event dict with key "model_filepath". Event received = {}'.format(event))
            return
        
        # ********************************************* #
        # *** ESTIMATING PRICE/DURATION WITH SLICER *** #
        # ********************************************* #

        try:
            complete_process = subprocess.run(command, shell=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
            
            if complete_process.returncode == 1:
            
                error_message = 'Error occurred in subprocess command'

                output_lines = str(complete_process.stdout).split('\\n')
                for output_line in output_lines:
                    if output_line.startswith('error'):
                        output_line_split = output_line.split(': ', 1)

                        if len(output_line) > 1:
                            error_message = output_line_split[1]
                
                if os.path.isfile(model_filepath):
                    os.remove(model_filepath)

                await self.send(text_data=json.dumps({'error': error_message}))
                await self.disconnect()
            
        except subprocess.CalledProcessError as e:
            if os.path.isfile(model_filepath):
                os.remove(model_filepath)

            await self.send(text_data=json.dumps({'error': str(e)}))
            await self.disconnect()
        
        # ************************************ #
        # *** .GCODE ESTIMATION EXTRACTION *** #
        # ************************************ #

        model_filepath_without_suffix = os.path.splitext(model_filepath)[0]
        gcode_paths = glob.glob("{}*gcode".format(model_filepath_without_suffix))

        if not gcode_paths:
            if os.path.isfile(model_filepath):
                os.remove(model_filepath)

            await self.send(text_data=json.dumps({'error': '.gcode files not found in directory'}))
            await self.disconnect()

        if len(gcode_paths) > 1:
            if os.path.isfile(model_filepath):
                os.remove(model_filepath)
            
            await self.send(text_data=json.dumps({'error': 'Duplicated .gcode files'}))
            await self.disconnect()

        gcode_path = gcode_paths[0]
        gcode_filename = os.path.basename(gcode_path)
        gcode_filename_without_suffix = os.path.splitext(gcode_filename)[0]

        estimated_duration_raw = gcode_filename_without_suffix.split('_')[-3]
        estimated_price_raw = gcode_filename_without_suffix.split('_')[-1]

        pattern = re.compile(r"(\d+d)?(\d+h)?(\d+m)?")
        estimated_duration_split = pattern.search(estimated_duration_raw).groups()
        if len(estimated_duration_split) != 3:

            if os.path.isfile(model_filepath):
                os.remove(model_filepath)
            if os.path.isfile(gcode_path):
                os.remove(gcode_path)

            await self.send(text_data={'error': 'Split DHM format invalid length. Expected 3, got {}'.format(len(estimated_duration_split))})
            await self.disconnect()

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

            if os.path.isfile(model_filepath):
                os.remove(model_filepath)
            if os.path.isfile(gcode_path):
                os.remove(gcode_path)

            await self.send(text_data={'error': 'Error while parsing duration DHM format: raw value = {}'.format(estimated_duration_raw)})
            await self.disconnect()

        estimated_price = float(estimated_price_raw)

        await self.send(text_data={'data': json.dumps({'estimated_time': estimated_duration, 'estimated_price': estimated_price})})
        await self.disconnect()
