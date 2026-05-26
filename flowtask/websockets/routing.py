# websockets/routing.py
# Enrutamiento específico para WebSockets de la app websockets
# NOTA: Este archivo está referenciado desde core/routing.py

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(
        r'ws/board/(?P<board_id>\d+)/$',
        consumers.BoardConsumer.as_asgi(),
        name='board-websocket'
    ),
    re_path(
        r'ws/notifications/$',
        consumers.NotificationConsumer.as_asgi(),
        name='notification-websocket'
    ),
]