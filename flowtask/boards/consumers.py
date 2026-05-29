# boards/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Board, Card, List, Comment, Notification, Activity


class BoardConsumer(AsyncWebsocketConsumer):
    """Consumer WebSocket para manejar eventos en tiempo real de un tablero"""
    
    async def connect(self):
        """Se ejecuta cuando un cliente WebSocket se conecta"""
        self.board_id = self.scope['url_route']['kwargs']['board_id']
        self.room_group_name = f'board_{self.board_id}'
        
        # DEBUG: Ver qué está pasando con el usuario
        print(f"🔍 User: {self.scope['user']}")
        print(f"🔍 User ID: {self.scope['user'].id if not self.scope['user'].is_anonymous else 'Anonymous'}")
        print(f"🔍 Is authenticated: {not self.scope['user'].is_anonymous}")
        
        # Verificar que el usuario está autenticado
        if self.scope['user'].is_anonymous:
            print(f"❌ Conexión rechazada: usuario anónimo")
            await self.close(code=4001)
            return
        
        # Verificar que el usuario es miembro del tablero
        is_member = await self.is_member(self.scope['user'].id, self.board_id)
        print(f"🔍 Is member of board {self.board_id}: {is_member}")
        
        if not is_member:
            print(f"❌ Conexión rechazada: usuario {self.scope['user'].email} no es miembro del board {self.board_id}")
            await self.close(code=4003)
            return
        
        # Unirse al grupo del tablero
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        print(f"✅ Usuario {self.scope['user'].email} conectado al board {self.board_id}")
    
    async def disconnect(self, close_code):
        """Se ejecuta cuando el cliente se desconecta"""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f"🔌 Usuario desconectado del board {self.board_id}, código: {close_code}")
    
    async def receive(self, text_data):
        """Recibe mensajes del cliente WebSocket"""
        data = json.loads(text_data)
        event_type = data.get('type')
        
        print(f"📨 Evento recibido: {event_type}")
        
        # Manejar diferentes tipos de eventos
        if event_type == 'task_moved':
            await self.handle_task_moved(data)
        elif event_type == 'comment_added':
            await self.handle_comment_added(data)
        elif event_type == 'notification_sent':
            await self.handle_notification_sent(data)
    
    async def handle_task_moved(self, data):
        """Manejar evento de tarea movida"""
        task_id = data.get('task_id')
        new_list_id = data.get('new_list_id')
        new_position = data.get('new_position', 0)
        user_id = self.scope['user'].id  # Usar el usuario autenticado
        
        print(f"🔄 Moviendo tarea {task_id} a lista {new_list_id}")
        
        # Actualizar la tarjeta en la base de datos
        success = await self.update_task_position(task_id, new_list_id, new_position)
        
        if success:
            # Registrar actividad
            await self.create_activity(
                board_id=self.board_id,
                user_id=user_id,
                action_type='task_moved',
                task_id=task_id,
                details={'new_list_id': new_list_id, 'position': str(new_position)}
            )
            
            # Notificar a todos en el grupo
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'task_moved_broadcast',
                    'task_id': task_id,
                    'new_list_id': new_list_id,
                    'new_position': str(new_position),
                    'user_id': user_id,
                    'timestamp': data.get('timestamp')
                }
            )
    
    async def handle_comment_added(self, data):
        """Manejar evento de nuevo comentario"""
        task_id = data.get('task_id')
        content = data.get('content')
        author_id = self.scope['user'].id  # Usar el usuario autenticado
        
        print(f"💬 Nuevo comentario en tarea {task_id}")
        
        # Crear comentario en BD
        comment = await self.create_comment(task_id, author_id, content)
        
        if comment:
            # Registrar actividad
            await self.create_activity(
                board_id=self.board_id,
                user_id=author_id,
                action_type='comment_added',
                task_id=task_id,
                details={'comment_preview': content[:50]}
            )
            
            # Notificar a todos
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'comment_broadcast',
                    'task_id': task_id,
                    'comment': {
                        'id': comment['id'],
                        'content': comment['content'],
                        'author': comment['author'],
                        'author_id': comment['author_id'],
                        'created_at': comment['created_at']
                    }
                }
            )
    
    async def task_moved_broadcast(self, event):
        """Enviar evento de tarea movida a todos los clientes"""
        await self.send(text_data=json.dumps({
            'type': 'task_moved',
            'task_id': event['task_id'],
            'new_list_id': event['new_list_id'],
            'new_position': event['new_position'],
            'user_id': event['user_id'],
            'timestamp': event['timestamp']
        }))
    
    async def comment_broadcast(self, event):
        """Enviar nuevo comentario a todos los clientes"""
        await self.send(text_data=json.dumps({
            'type': 'new_comment',
            'task_id': event['task_id'],
            'comment': event['comment']
        }))
    
    # ========== MÉTODOS SINCRÓNICOS PARA BASE DE DATOS ==========
    
    @database_sync_to_async
    def is_member(self, user_id, board_id):
        """Verificar si el usuario es miembro del tablero o es el owner"""
        try:
            board = Board.objects.get(id=board_id)
            # El owner también puede conectarse
            if board.owner.id == user_id:
                return True
            return board.members.filter(id=user_id).exists()
        except Board.DoesNotExist:
            return False
    
    @database_sync_to_async
    def update_task_position(self, task_id, new_list_id, new_position):
        """Actualizar la posición de una tarjeta"""
        try:
            task = Card.objects.get(id=task_id)
            task.list_id = new_list_id
            task.position = new_position
            task.save()
            print(f"✅ Tarea {task_id} actualizada a lista {new_list_id}, posición {new_position}")
            return True
        except Card.DoesNotExist:
            print(f"❌ Tarea {task_id} no encontrada")
            return False
    
    @database_sync_to_async
    def create_comment(self, task_id, author_id, content):
        """Crear un nuevo comentario"""
        from django.utils import timezone
        try:
            task = Card.objects.get(id=task_id)
            author = User.objects.get(id=author_id)
            comment = Comment.objects.create(
                task=task,
                author=author,
                content=content
            )
            print(f"✅ Comentario creado en tarea {task_id}")
            return {
                'id': comment.id,
                'content': comment.content,
                'author': author.username,
                'author_id': author.id,
                'created_at': timezone.now().isoformat()
            }
        except Card.DoesNotExist:
            print(f"❌ Tarea {task_id} no encontrada para comentario")
            return None
        except User.DoesNotExist:
            print(f"❌ Usuario {author_id} no encontrado")
            return None
    
    @database_sync_to_async
    def create_activity(self, board_id, user_id, action_type, task_id=None, details=None):
        """Registrar una actividad"""
        try:
            board = Board.objects.get(id=board_id)
            user = User.objects.get(id=user_id)
            task = Card.objects.get(id=task_id) if task_id else None
            
            Activity.objects.create(
                board=board,
                user=user,
                action_type=action_type,
                task=task,
                details=details or {}
            )
            print(f"✅ Actividad registrada: {action_type}")
        except Exception as e:
            print(f"❌ Error al registrar actividad: {e}")


class NotificationConsumer(AsyncWebsocketConsumer):
    """Consumer para notificaciones personales del usuario"""
    
    async def connect(self):
        self.user_id = self.scope['user'].id
        self.user_group = f'user_{self.user_id}_notifications'
        
        print(f"🔍 NotificationConsumer - User: {self.scope['user']}")
        
        if self.scope['user'].is_anonymous:
            print(f"❌ NotificationConsumer rechazado: usuario anónimo")
            await self.close(code=4001)
            return
        
        await self.channel_layer.group_add(
            self.user_group,
            self.channel_name
        )
        await self.accept()
        print(f"✅ NotificationConsumer conectado para usuario {self.scope['user'].email}")
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.user_group,
            self.channel_name
        )
        print(f"🔌 NotificationConsumer desconectado")
    
    async def send_notification(self, event):
        """Enviar notificación al usuario"""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': event['notification']
        }))