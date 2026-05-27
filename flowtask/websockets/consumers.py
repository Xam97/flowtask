# websockets/consumers.py
# Consumers base para WebSockets con Django Channels
# Esta fase solo prepara la estructura, la lógica realtime se implementará después

import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from boards.models import Board, Membership

# ========== CONSUMER DE TABLERO ==========
class BoardConsumer(AsyncJsonWebsocketConsumer):
    """
    Consumer para manejar WebSockets de un tablero específico.
    Manejará:
    - Movimiento de tarjetas en tiempo real
    - Publicación de comentarios
    - Actualizaciones de actividad
    
    En esta fase solo implementa conexión/desconexión y verificación de permisos.
    """
    
    async def connect(self):
        """
        Se ejecuta cuando un cliente intenta conectar al WebSocket.
        Verifica:
        1. Usuario autenticado
        2. El usuario tiene permiso para acceder al tablero
        3. El tablero existe
        """
        self.board_id = self.scope['url_route']['kwargs']['board_id']
        self.room_group_name = f'board_{self.board_id}'
        
        # Verificar autenticación
        user = self.scope['user']
        if user.is_anonymous:
            # Rechazar conexión si no está autenticado
            await self.close()
            return
        
        # Verificar que el usuario tiene acceso al tablero
        has_access = await self.check_board_access(user.id, self.board_id)
        if not has_access:
            await self.close()
            return
        
        # Unirse al grupo del tablero
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # Aceptar la conexión WebSocket
        await self.accept()
    
    async def disconnect(self, close_code):
        """
        Se ejecuta cuando el cliente se desconecta.
        Remueve al cliente del grupo.
        """
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
    
    async def receive_json(self, content):
        """
        Recibe mensajes JSON del cliente.
        En esta fase solo preparamos la estructura.
        Los handlers específicos se implementarán en la fase 2.
        """
        message_type = content.get('type')
        
        # Preparación para futuros handlers
        if message_type == 'card_move':
            # TODO: Implementar en fase 2
            pass
        elif message_type == 'new_comment':
            # TODO: Implementar en fase 2
            pass
        elif message_type == 'card_update':
            # TODO: Implementar en fase 2
            pass
    
    async def board_update(self, event):
        """
        Envía actualizaciones del tablero a todos los clientes conectados.
        """
        await self.send_json(event['data'])
    
    @database_sync_to_async
    def check_board_access(self, user_id, board_id):
        """
        Verifica si un usuario tiene acceso a un tablero.
        Esta verificación es CRÍTICA para la seguridad.
        """
        try:
            board = Board.objects.get(id=board_id, is_archived=False)
            # El usuario puede ser owner o miembro
            return board.owner_id == user_id or board.members.filter(id=user_id).exists()
        except Board.DoesNotExist:
            return False

# ========== CONSUMER DE NOTIFICACIONES ==========
class NotificationConsumer(AsyncJsonWebsocketConsumer):
    """
    Consumer para manejar notificaciones en tiempo real de un usuario específico.
    """
    
    async def connect(self):
        """
        Conecta al usuario a su canal personal de notificaciones.
        """
        user = self.scope['user']
        if user.is_anonymous:
            await self.close()
            return
        
        self.user_id = user.id
        self.room_group_name = f'notifications_{self.user_id}'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        """
        Desconecta del canal de notificaciones.
        """
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
    
    async def send_notification(self, event):
        """
        Envía una notificación al usuario.
        """
        await self.send_json(event['data'])
