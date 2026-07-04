# core/asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.utils import timezone
import re

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Obtener la aplicación Django normal para HTTP
django_asgi_app = get_asgi_application()

# Importar routing después de configurar Django
from boards.routing import websocket_urlpatterns

class SessionAuthMiddleware(BaseMiddleware):
    """Middleware para autenticar WebSockets usando la cookie de sesión de Django"""
    
    async def __call__(self, scope, receive, send):
        print("=" * 50)
        print(" MIDDLEWARE: Entrando al middleware de sesión")
        
        # Extraer cookies del scope de manera más robusta
        cookies = {}
        headers = dict(scope.get('headers', []))
        
        if b'cookie' in headers:
            cookie_header = headers[b'cookie'].decode()
            print(f" Cookie header completo: {cookie_header}")
            
            # Parsear cookies correctamente (manejando espacios y formato)
            for cookie in cookie_header.split(';'):
                cookie = cookie.strip()
                if '=' in cookie:
                    key, value = cookie.split('=', 1)
                    cookies[key.strip()] = value.strip()
            
            print(f" Todas las cookies parseadas: {list(cookies.keys())}")
            
            # Buscar sessionid (posibles variaciones)
            session_key = cookies.get('sessionid') or cookies.get('session_id')
            print(f" Session key encontrada: {session_key}")
        else:
            print(" No hay header 'cookie'")
            session_key = None
        
        if session_key:
            try:
                user = await self.get_user_from_session(session_key)
                if user:
                    scope['user'] = user
                    print(f" Usuario autenticado: {user.email}")
                else:
                    print(f" Usuario no encontrado para sesión: {session_key}")
                    from django.contrib.auth.models import AnonymousUser
                    scope['user'] = AnonymousUser()
            except Exception as e:
                print(f" Error: {e}")
                from django.contrib.auth.models import AnonymousUser
                scope['user'] = AnonymousUser()
        else:
            print(f" No se encontró 'sessionid' en cookies")
            print(f" Cookies disponibles: {cookies}")
            from django.contrib.auth.models import AnonymousUser
            scope['user'] = AnonymousUser()
        
        print("=" * 50)
        return await super().__call__(scope, receive, send)
    
    @database_sync_to_async
    def get_user_from_session(self, session_key):
        """Obtener usuario desde la session key de Django"""
        try:
            session = Session.objects.get(session_key=session_key, expire_date__gt=timezone.now())
            session_data = session.get_decoded()
            user_id = session_data.get('_auth_user_id')
            
            if user_id:
                user = User.objects.get(id=user_id)
                print(f" Usuario encontrado: {user.email}")
                return user
            else:
                print(f" No hay _auth_user_id en sesión")
                return None
        except Session.DoesNotExist:
            print(f" Sesión no encontrada: {session_key}")
            return None
        except User.DoesNotExist:
            print(f" Usuario no encontrado para ID: {user_id}")
            return None

# Configurar la aplicación
application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': SessionAuthMiddleware(
        URLRouter(websocket_urlpatterns)
    ),
})