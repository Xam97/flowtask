# core/routing.py
# Enrutamiento principal de WebSockets
# IMPORTANTE: Este archivo debe existir en la app core

from django.urls import re_path, include

# Importar websocket_urlpatterns desde la app websockets
# Esto permite mantener el enrutamiento modular
websocket_urlpatterns = [
    # Incluir todos los patrones de la app websockets
    re_path(r'^', include('websockets.routing')),
]