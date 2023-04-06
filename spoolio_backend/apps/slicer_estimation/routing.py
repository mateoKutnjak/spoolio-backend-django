from django.urls import path

from . import consumers


websocket_urlpatterns = [
    path("ws/slicer-estimation/", consumers.SlicerEstimationConsumer.as_asgi()),
]