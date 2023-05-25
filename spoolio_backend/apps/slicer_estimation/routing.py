from django.urls import path

from . import consumers


websocket_urlpatterns = [
    path("ws/print-order/estimation/slicer-and-print-job-ending-time/", consumers.SlicerEstimationConsumer.as_asgi()),
    path("ws/print-order/estimation/print-job-ending-time/", consumers.PrintJobEndingTimeEstimationConsumer.as_asgi()),
]