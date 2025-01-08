import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.layers import get_channel_layer
from django.urls import path
import django

django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            # Define WebSocket URL routing here
            path("ws/notifications/", consumers.NotificationConsumer.as_asgi()),
        ])
    ),
})
