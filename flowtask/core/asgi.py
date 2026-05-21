
# Permite manejar conexiones en tiempo real

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Importar routing después de configurar el entorno
from core.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    # HTTP: Manejo de peticiones normales
    "http": get_asgi_application(),
    
    # WebSocket: Manejo de conexiones en tiempo real
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
})