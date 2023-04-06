import json
import logging
import uuid

from channels.generic.websocket import AsyncWebsocketConsumer


logger = logging.getLogger(__name__)


class SlicerEstimationConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        self.group_group_name = str(uuid.uuid4())

        await self.channel_layer.group_add(
            self.group_group_name,
            self.channel_name
        )

        await self.accept()
        await self.send(text_data=json.dumps({
            "type": "init",
            "meta": {
                "channel_group_name": self.group_group_name, 
            }
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_group_name, self.channel_name)

    async def receive(self, text_data):
        # TODO
        print("WEBSOCKET CONSUMER RECEIVE")
        print(text_data)
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        self.send(text_data=json.dumps({"message": message}))

    async def slicer_estimation(self, event):
        # TODO
        print('0000000000000000')
        print(event)