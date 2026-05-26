# Consumers para WebSockets con Django Channels

import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from boards.models import Board, List, Card


# ========== CONSUMER DE TABLERO ==========
class BoardConsumer(AsyncJsonWebsocketConsumer):
    """
    Consumer para manejar WebSockets de un tablero específico.
    Maneja:
    - Movimiento de tarjetas en tiempo real
    - Actualizaciones de tarjetas
    - Creación y eliminación de tarjetas
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
        
        # Enviar mensaje de bienvenida
        await self.send_json({
            'type': 'connection_established',
            'message': f'Conectado al tablero {self.board_id}',
            'board_id': self.board_id
        })
    
    async def disconnect(self, close_code):
        """
        Se ejecuta cuando el cliente se desconecta.
        """
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
    
    async def receive_json(self, content):
        """
        Recibe mensajes JSON del cliente.
        """
        message_type = content.get('type')
        user = self.scope['user']
        
        # Manejar movimiento de tarjeta
        if message_type == 'card_move':
            await self.handle_card_move(content, user)
        
        # Manejar actualización de tarjeta
        elif message_type == 'card_update':
            await self.handle_card_update(content, user)
        
        # Manejar creación de tarjeta
        elif message_type == 'card_create':
            await self.handle_card_create(content, user)
        
        # Manejar eliminación de tarjeta
        elif message_type == 'card_delete':
            await self.handle_card_delete(content, user)
        
        # Manejar ping (keepalive)
        elif message_type == 'ping':
            await self.send_json({'type': 'pong'})
    
    async def handle_card_move(self, content, user):
        """
        Maneja el movimiento de una tarjeta entre listas
        """
        card_id = content.get('card_id')
        new_list_id = content.get('list_id')
        new_position = content.get('position')
        
        try:
            # Actualizar la tarjeta en la base de datos
            card = await self.get_card(card_id)
            if card:
                await self.update_card_position(card, new_list_id, new_position)
                
                # Notificar a todos en el tablero
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'card_moved',
                        'data': {
                            'card_id': card_id,
                            'list_id': new_list_id,
                            'position': new_position,
                            'moved_by': user.username,
                            'card_title': card.title
                        }
                    }
                )
        except Exception as e:
            await self.send_json({
                'type': 'error',
                'message': f'Error al mover tarjeta: {str(e)}'
            })
    
    async def handle_card_update(self, content, user):
        """
        Maneja la actualización de una tarjeta
        """
        card_id = content.get('card_id')
        field = content.get('field')
        value = content.get('value')
        
        try:
            await self.update_card_field(card_id, field, value)
            
            # Notificar a todos en el tablero
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'card_updated',
                    'data': {
                        'card_id': card_id,
                        'field': field,
                        'value': value,
                        'updated_by': user.username
                    }
                }
            )
        except Exception as e:
            await self.send_json({
                'type': 'error',
                'message': f'Error al actualizar tarjeta: {str(e)}'
            })
    
    async def handle_card_create(self, content, user):
        """
        Maneja la creación de una nueva tarjeta
        """
        list_id = content.get('list_id')
        title = content.get('title')
        description = content.get('description', '')
        
        try:
            card = await self.create_new_card(
                list_id=list_id,
                title=title,
                description=description,
                created_by=user
            )
            
            # Notificar a todos en el tablero
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'card_created',
                    'data': {
                        'card_id': card.id,
                        'title': card.title,
                        'description': card.description,
                        'list_id': list_id,
                        'created_by': user.username,
                        'position': float(card.position)
                    }
                }
            )
        except Exception as e:
            await self.send_json({
                'type': 'error',
                'message': f'Error al crear tarjeta: {str(e)}'
            })
    
    async def handle_card_delete(self, content, user):
        """
        Maneja la eliminación de una tarjeta
        """
        card_id = content.get('card_id')
        
        try:
            card = await self.get_card(card_id)
            if card:
                card_title = card.title
                await self.delete_card(card_id)
                
                # Notificar a todos en el tablero
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'card_deleted',
                        'data': {
                            'card_id': card_id,
                            'deleted_by': user.username,
                            'card_title': card_title
                        }
                    }
                )
        except Exception as e:
            await self.send_json({
                'type': 'error',
                'message': f'Error al eliminar tarjeta: {str(e)}'
            })
    
    # ========== MÉTODOS DE NOTIFICACIÓN AL GRUPO ==========
    
    async def card_moved(self, event):
        """Envía actualización de movimiento de tarjeta"""
        await self.send_json({
            'type': 'card_moved',
            'data': event['data']
        })
    
    async def card_updated(self, event):
        """Envía actualización de tarjeta"""
        await self.send_json({
            'type': 'card_updated',
            'data': event['data']
        })
    
    async def card_created(self, event):
        """Envía creación de tarjeta"""
        await self.send_json({
            'type': 'card_created',
            'data': event['data']
        })
    
    async def card_deleted(self, event):
        """Envía eliminación de tarjeta"""
        await self.send_json({
            'type': 'card_deleted',
            'data': event['data']
        })
    
    # ========== MÉTODOS DE BASE DE DATOS (ASYNC) ==========
    
    @database_sync_to_async
    def check_board_access(self, user_id, board_id):
        """Verifica si un usuario tiene acceso a un tablero"""
        try:
            board = Board.objects.get(id=board_id, is_archived=False)
            return board.owner_id == user_id or board.members.filter(id=user_id).exists()
        except Board.DoesNotExist:
            return False
    
    @database_sync_to_async
    def get_card(self, card_id):
        """Obtiene una tarjeta por ID"""
        try:
            return Card.objects.get(id=card_id)
        except Card.DoesNotExist:
            return None
    
    @database_sync_to_async
    def update_card_position(self, card, new_list_id, new_position):
        """Actualiza la posición de una tarjeta"""
        card.list_id = new_list_id
        card.position = float(new_position)
        card.save()
        return True
    
    @database_sync_to_async
    def update_card_field(self, card_id, field, value):
        """Actualiza un campo específico de una tarjeta"""
        card = Card.objects.get(id=card_id)
        setattr(card, field, value)
        card.save()
    
    @database_sync_to_async
    def create_new_card(self, list_id, title, description, created_by):
        """Crea una nueva tarjeta"""
        from django.db import models
        list_obj = List.objects.get(id=list_id)
        max_position = Card.objects.filter(list=list_obj).aggregate(
            models.Max('position')
        )['position__max'] or 0
        
        return Card.objects.create(
            title=title,
            description=description,
            list=list_obj,
            created_by=created_by,
            position=max_position + 10
        )
    
    @database_sync_to_async
    def delete_card(self, card_id):
        """Elimina una tarjeta"""
        Card.objects.filter(id=card_id).delete()


# ========== CONSUMER DE NOTIFICACIONES ==========
class NotificationConsumer(AsyncJsonWebsocketConsumer):
    """
    Consumer para manejar notificaciones en tiempo real de un usuario específico.
    Versión simplificada.
    """
    
    async def connect(self):
        """Conecta al usuario a su canal personal de notificaciones"""
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
        
        # Enviar mensaje de bienvenida
        await self.send_json({
            'type': 'connection_established',
            'message': 'Conectado a notificaciones'
        })
    
    async def disconnect(self, close_code):
        """Desconecta del canal de notificaciones"""
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
    
    async def send_notification(self, event):
        """Envía una notificación al usuario"""
        await self.send_json({
            'type': 'notification',
            'data': event['data']
        })