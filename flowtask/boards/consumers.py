# boards/consumers.py
# Consumers para WebSockets

import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Board, List, Card
from .permissions import user_has_permission


class BoardConsumer(AsyncJsonWebsocketConsumer):
    """Consumer para WebSockets del tablero"""
    
    async def connect(self):
        self.board_id = self.scope['url_route']['kwargs']['board_id']
        self.room_group_name = f'board_{self.board_id}'
        
        user = self.scope['user']
        if user.is_anonymous:
            await self.close()
            return
        
        has_access = await self.check_board_access(user.id, self.board_id)
        if not has_access:
            await self.close()
            return
        
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        
        await self.send_json({
            'type': 'connection_established',
            'message': f'Conectado al tablero {self.board_id}'
        })
    
    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
    
    async def receive_json(self, content):
        message_type = content.get('type')
        user = self.scope['user']
        
        if message_type == 'card_move':
            await self.handle_card_move(content, user)
    
    async def handle_card_move(self, content, user):
        card_id = content.get('card_id')
        new_list_id = content.get('list_id')
        new_position = content.get('position')
        
        try:
            card = await self.get_card(card_id)
            if card:
                can_move = await self.check_move_permission(user.id, card)
                if not can_move:
                    await self.send_json({'type': 'error', 'message': 'Sin permiso para mover tarjetas'})
                    return

                await self.update_card_position(card, new_list_id, new_position)
                
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
            await self.send_json({'type': 'error', 'message': str(e)})
    
    async def card_moved(self, event):
        await self.send_json({'type': 'card_moved', 'data': event['data']})

    async def new_comment(self, event):
        await self.send_json({'type': 'new_comment', 'data': event['data']})

    async def comment_deleted(self, event):
        await self.send_json({'type': 'comment_deleted', 'data': event['data']})
    
    @database_sync_to_async
    def check_board_access(self, user_id, board_id):
        try:
            board = Board.objects.get(id=board_id, is_archived=False)
            return board.owner_id == user_id or board.members.filter(id=user_id).exists()
        except Board.DoesNotExist:
            return False
    
    @database_sync_to_async
    def check_move_permission(self, user_id, card):
        try:
            user = User.objects.get(id=user_id)
            board = card.list.board
            return user_has_permission(user, board, 'move_card')
        except User.DoesNotExist:
            return False
    
    @database_sync_to_async
    def get_card(self, card_id):
        try:
            return Card.objects.get(id=card_id)
        except Card.DoesNotExist:
            return None
    
    @database_sync_to_async
    def update_card_position(self, card, new_list_id, new_position):
        card.list_id = new_list_id
        card.position = float(new_position)
        card.save()


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    """Consumer para notificaciones personales - Versión simplificada"""
    
    async def connect(self):
        user = self.scope['user']
        if user.is_anonymous:
            await self.close()
            return
        
        self.user_id = user.id
        self.room_group_name = f'notifications_{self.user_id}'
        
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        
        await self.send_json({
            'type': 'connection_established',
            'message': 'Conectado a notificaciones'
        })
    
    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
    
    async def send_notification(self, event):
        """Recibe el evento del group_send y lo manda limpio al JS"""
        await self.send_json({
            'type': 'notification',             
            'notification': event['notification'] 
        })