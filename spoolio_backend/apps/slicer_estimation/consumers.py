from enum import Enum
import json
import logging
import uuid

from channels.generic.websocket import AsyncWebsocketConsumer


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
        await self.sendInitMessage()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.channel_group_name, self.channel_name)

    async def slicer_estimation_success(self, event):
        estimated_price = event.get('payload', {}).get('data', {}).get('estimated_price')
        estimated_time = event.get('payload', {}).get('data', {}).get('estimated_time')

        if estimated_time and estimated_price:
            await self.sendDataMessage(estimated_time, estimated_price)
        else:
            await self.sendErrorMessage('Not all data is present (estimated_time={}, estimated_price={})'.format(estimated_time, estimated_price))

    async def slicer_estimation_error(self, event):
        error_message = event.get('payload', {}).get('message')
        await self.sendErrorMessage(error_message, close=True)

    async def sendInitMessage(self):
        message = {
            "type": WebsocketMessageType.INIT.value,
            "data": {
                "channel_group_name": self.channel_group_name, 
            }
        }

        logger.info('Websockets group {}'.format(self.channel_group_name))
        if hasattr(self, 'model_filepath'): 
            logger.info('   model file: {}'.format(self.model_filepath))
        logger.info('   message: {}'.format(message))

        await self.send(text_data=json.dumps(message))

    async def sendDataMessage(self, estimated_time: int, estimated_price: float):
        message = {
            "type": WebsocketMessageType.DATA.value,
            "data": {
                "estimated_time": estimated_time, 
                "estimated_price": estimated_price,
            }
        }

        logger.info('Websockets group {}'.format(self.channel_group_name))
        if hasattr(self, 'model_filepath'): 
            logger.info('   model file: {}'.format(self.model_filepath))
        logger.info('   message: {}'.format(message))

        await self.send(text_data=json.dumps(message))

    async def sendErrorMessage(self, error_message: str, close=False):
        message = {
            "type": WebsocketMessageType.ERROR.value,
            "error": error_message
        }

        logger.info('Websockets group {}'.format(self.channel_group_name))
        if hasattr(self, 'model_filepath'): 
            logger.info('   model file: {}'.format(self.model_filepath))
        logger.info('   message: {}'.format(message))

        await self.send(text_data=json.dumps(message))

        if close:
            await self.close()