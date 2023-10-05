from enum import Enum
import json
import logging
import uuid

from channels.generic.websocket import AsyncWebsocketConsumer

from .. print_job import tasks as print_job_tasks

from ... libs import channels


logger = logging.getLogger(__name__)


class WebsocketMessageType(Enum):
    INIT = 'init'
    DATA = 'data'
    ERROR = 'error'
    CLOSE = 'close'


class PrintJobEndingTimeEstimationConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        self.channel_group_name = str(uuid.uuid4())

        await self.channel_layer.group_add(
            self.channel_group_name,
            self.channel_name
        )

        await self.accept()

    async def receive(self, text_data=None, bytes_data=None):

        # TODO generate_celery_delay_request function

        print_job_tasks.print_job_ending_time_estimation.delay({
            'meta': {
                'django_channels': {
                    'channel_group_name': self.channel_group_name
                }
            },
            'data': {
                'units': json.loads(text_data)
            }
        })

    async def on_success(self, event):
        estimated_ending_time = event.get('payload', {}).get(
            'data', {}).get('estimated_ending_time')
        job_ids = event.get('payload', {}).get(
            'data', {}).get('job_ids')

        if estimated_ending_time:
            data = {
                "estimated_ending_time": estimated_ending_time,
                "job_ids": job_ids
            }

            await self.send(text_data=channels.generate_data_response(data))
        else:
            error_message = 'Not all data is present (estimated_ending_time={})'.format(
                estimated_ending_time)
            await self.send(text_data=channels.generate_error_response(error_message))

        await self.channel_layer.group_discard(self.channel_group_name, self.channel_name)

    async def on_error(self, event):

        error_message = event.get('payload', {}).get('message')

        await self.send(text_data=channels.generate_error_response(error_message))
        await self.close()

        await self.channel_layer.group_discard(self.channel_group_name, self.channel_name)


class SlicerEstimationConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        self.channel_group_name = str(uuid.uuid4())

        await self.channel_layer.group_add(
            self.channel_group_name,
            self.channel_name
        )

        await self.accept()
        await self.send(text_data=channels.generate_init_response(self.channel_group_name))

    async def on_success(self, event):
        estimated_price = event.get('payload', {}).get(
            'data', {}).get('estimated_price')
        estimated_time = event.get('payload', {}).get(
            'data', {}).get('estimated_time')
        pricing_list = event.get('payload', {}).get(
            'data', {}).get('pricing_list')

        if estimated_time and estimated_price and pricing_list:

            data = {
                "estimated_time": estimated_time,
                "estimated_price": estimated_price,
                "pricing_list": pricing_list
            }

            await self.send(text_data=channels.generate_data_response(data))
        else:
            error_message = 'Not all data is present (estimated_time={}, estimated_price={}, pricing_list={})'.format(
                estimated_time, estimated_price, pricing_list)
            await self.send(text_data=channels.generate_error_response(error_message))

        await self.channel_layer.group_discard(self.channel_group_name, self.channel_name)

    async def on_error(self, event):
        error_message = event.get('payload', {}).get('message')

        await self.send(text_data=channels.generate_error_response(error_message))
        await self.close()

        await self.channel_layer.group_discard(self.channel_group_name, self.channel_name)
