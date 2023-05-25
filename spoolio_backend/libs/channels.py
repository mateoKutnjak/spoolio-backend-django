import json
import logging

from asgiref.sync import async_to_sync

from channels.layers import get_channel_layer


logger = logging.getLogger(__name__)


def channels_group_send_error(error_message, channel_group_name):
    logger.error(error_message)
    
    if channel_group_name:
        channel_layer = get_channel_layer()

        async_to_sync(channel_layer.group_send)(channel_group_name, {
            "type": 'on.error',
            "payload": {
                "type": 'error',
                "message": error_message
            }
        })

def channels_group_send_data(data, channel_group_name):
    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(channel_group_name, {
        "type": "on.success",
        "payload": {
            "type": 'success',
            "data": data
        }
    })

def generate_error_response(error_message):
    return json.dumps({
        "type": 'error',
        "error": error_message
    })

def generate_data_response(data):
    return json.dumps({
        "type": 'data',
        "data": data
    })

def generate_init_response(channel_group_name):
    return json.dumps({
        "type": 'init',
        "data": {
            "channel_group_name": channel_group_name, 
        }
    })