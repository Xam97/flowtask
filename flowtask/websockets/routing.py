<<<<<<< HEAD
# websockets/routing.py
# Enrutamiento específico para WebSockets de la app websockets
# NOTA: Este archivo está referenciado desde core/routing.py
=======
# Enrutamiento específico para WebSockets de la app websockets
>>>>>>> origin/camilarodas

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
<<<<<<< HEAD
=======
    # WebSocket para un tablero específico
>>>>>>> origin/camilarodas
    re_path(
        r'ws/board/(?P<board_id>\d+)/$',
        consumers.BoardConsumer.as_asgi(),
        name='board-websocket'
    ),
<<<<<<< HEAD
=======
    
    # WebSocket para notificaciones personales
>>>>>>> origin/camilarodas
    re_path(
        r'ws/notifications/$',
        consumers.NotificationConsumer.as_asgi(),
        name='notification-websocket'
    ),
]