# Enrutamiento principal de WebSockets - Importa rutas desde websockets

from django.urls import re_path, include
from websockets import consumers

# Importar las rutas definidas en la app websockets
websocket_urlpatterns = [
    # WebSocket para actividad en tiempo real de un tablero específico
    # Ejemplo: ws://localhost:8000/ws/board/5/
    re_path(
        r'ws/board/(?P<board_id>\d+)/$',
        consumers.BoardConsumer.as_asgi(),
        name='board-websocket'
    ),
    
    # WebSocket para notificaciones globales del usuario
    # Ejemplo: ws://localhost:8000/ws/notifications/
    re_path(
        r'ws/notifications/$',
        consumers.NotificationConsumer.as_asgi(),
        name='notification-websocket'
    ),

    # Incluir todos los patrones de la app websockets
    re_path(r'^', include('websockets.routing')),
]



