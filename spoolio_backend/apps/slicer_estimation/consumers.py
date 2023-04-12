import datetime
from enum import Enum
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


class WebsocketMessageType(Enum):
    INIT = 'init'
    DATA = 'data'
    ERROR = 'error'
    CLOSE = 'close'


class SlicerEstimationConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        self.channel_group_name = str(uuid.uuid4())

        await self.channel_layer.group_add(
            self.channel_group_name,
            self.channel_name
        )

        await self.accept()
        await self.sendInitMessage(self.channel_group_name)

    async def disconnect(self, close_code):
        # await self.sendCloseMessage("Close code = {}".format(close_code))
        await self.channel_layer.group_discard(self.channel_group_name, self.channel_name)

    async def slicer_estimation(self, event):

        # ******************************************** #
        # *** CHECK EVENT DATA DICTIONARY VALIDITY *** #
        # ******************************************** #

        command = event.get('prusa_slicer_bash_command')
        if not command:
            await self.sendErrorMessage(
                'Expected event dict with key "cmd". Event received = {}'.format(event),
                close=True
            )
            return
        
        self.model_filepath = event.get('3d_model_filepath')
        if not self.model_filepath:
            await self.sendErrorMessage(
                'Expected event dict with key "model_filepath". Event received = {}'.format(event),
                close=True
            )
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

                await self.sendErrorMessage(error_message, close=True)
                self.cleanFiles()
                return
            
        except subprocess.CalledProcessError as e:
            await self.sendErrorMessage(str(e), close=True)
            self.cleanFiles()
            return
        
        # ************************************ #
        # *** .GCODE ESTIMATION EXTRACTION *** #
        # ************************************ #

        model_filepath_without_suffix = os.path.splitext(self.model_filepath)[0]
        gcode_paths = glob.glob("{}*gcode".format(model_filepath_without_suffix))

        if not gcode_paths:
            await self.sendErrorMessage('.gcode files not found in directory', close=True)
            self.cleanFiles()
            return

        if len(gcode_paths) > 1:
            await self.sendErrorMessage('Duplicated .gcode files', close=True)
            self.cleanFiles()
            return

        self.gcode_path = gcode_paths[0]
        gcode_filename = os.path.basename(self.gcode_path)
        gcode_filename_without_suffix = os.path.splitext(gcode_filename)[0]

        estimated_duration_raw = gcode_filename_without_suffix.split('_')[-3]
        estimated_price_raw = gcode_filename_without_suffix.split('_')[-1]

        self.cleanFiles()

        pattern = re.compile(r"(\d+d)?(\d+h)?(\d+m)?")
        estimated_duration_split = pattern.search(estimated_duration_raw).groups()
        if len(estimated_duration_split) != 3:

            await self.sendErrorMessage( 'Split DHM format invalid length. Expected 3, got {}'.format(len(estimated_duration_split)), close=True)
            self.cleanFiles()
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
            await self.sendErrorMessage('Error while parsing duration DHM format: raw value = {}'.format(estimated_duration_raw), close=True)
            self.cleanFiles()
            return

        estimated_price = float(estimated_price_raw)

        await self.sendDataMessage(estimated_duration, estimated_price)
        await self.disconnect()

    async def sendInitMessage(self, channel_group_name: str):
        await self.send(text_data=json.dumps({
            "type": WebsocketMessageType.INIT.value,
            "data": {
                "channel_group_name": channel_group_name, 
            }
        }))

    async def sendDataMessage(self, estimated_time: int, estimated_price: float):
        await self.send(text_data=json.dumps({
            "type": WebsocketMessageType.DATA.value,
            "data": {
                "estimated_time": estimated_time, 
                "estimated_price": estimated_price,
            }
        }))

    async def sendErrorMessage(self, error_message: str, close=False):
        logger.error(error_message)

        await self.send(text_data=json.dumps({
            "type": WebsocketMessageType.ERROR.value,
            "error": error_message
        }))

        if close:
            await self.close()

    async def sendCloseMessage(self, reason):
        await self.send(text_data=json.dumps({
            "type": WebsocketMessageType.CLOSE.value,
            "data": {
                "reason": reason
            }
        }))

    def cleanFiles(self):
        if hasattr(self, 'model_filepath') and  os.path.isfile(self.model_filepath):
            os.remove(self.model_filepath)
        if hasattr(self, 'gcode_path') and os.path.isfile(self.gcode_path):
            os.remove(self.gcode_path)