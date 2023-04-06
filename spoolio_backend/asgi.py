"""
ASGI config for spoolio_backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

from spoolio_backend.apps.slicer_estimation import routing


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spoolio_backend.settings')

django_asgi_app = get_asgi_application()

print(routing.websocket_urlpatterns)

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            URLRouter(routing.websocket_urlpatterns)
        ),
    }
)