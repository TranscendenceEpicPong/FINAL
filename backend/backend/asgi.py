"""
ASGI config for backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from friends import routing as friend_routing
from blocks import routing as block_routing
from chats import routing as chat_routing
from game import routing as game_routing
from core import routing as core_routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

django_asgi_application = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_application,
    "websocket": 
        URLRouter([
            *friend_routing.websocket_urlpatterns,
            *block_routing.websocket_urlpatterns,
            *game_routing.websocket_urlpatterns,
            *chat_routing.websocket_urlpatterns,
            *core_routing.websocket_urlpatterns,
        ])
})