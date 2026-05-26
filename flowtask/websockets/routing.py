# Enrutamiento específico para WebSockets de la app websockets

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # WebSocket para un tablero específico
    re_path(
        r'ws/board/(?P<board_id>\d+)/$',
        consumers.BoardConsumer.as_asgi(),
        name='board-websocket'
    ),
    
    # WebSocket para notificaciones personales
    re_path(
        r'ws/notifications/$',
        consumers.NotificationConsumer.as_asgi(),
        name='notification-websocket'
    ),
]