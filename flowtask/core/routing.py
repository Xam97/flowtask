# Enrutamiento principal de WebSockets - Importa rutas desde websockets

from django.urls import path, include

# Importar las rutas definidas en la app websockets
websocket_urlpatterns = [
    path('ws/', include('websockets.routing')),
]