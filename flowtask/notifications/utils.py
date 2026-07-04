# notifications/utils.py
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification

def crear_notificacion(recipient, sender, notification_type, message=None, board_id=None, card_id=None):
    """
    Crea una notificación y la envía por WebSocket
    """
    if recipient == sender:
        return None
    
    if not message:
        message = _generar_mensaje_por_defecto(notification_type, sender)
        
    # 💡 Generar título por defecto para cumplir con el modelo
    titulos = {
        'task_assigned': 'Nueva Tarea',
        'comment_added': 'Nuevo Comentario',
        'task_moved': 'Tarea Movida',
        'mention': 'Mención',
        'member_added': 'Nuevo Tablero',
    }
    titulo_notificacion = titulos.get(notification_type, "Notificación")
    
    # Creación con todos los campos requeridos
    notification = Notification.objects.create(
        user=recipient,  
        sender=sender,      # 💡 Ahora sí existe en el modelo
        type=notification_type,  
        title=titulo_notificacion, # 💡 Insertado
        message=message,
        board_id=board_id,
        card_id=card_id
    )
    
    _enviar_websocket(recipient.id, notification)
    
    return notification


def _enviar_websocket(user_id, notification):
    """Envía notificación por WebSocket al usuario"""
    try:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'notifications_{user_id}',  # 💡 CORREGIDO: Ahora coincide exactamente con tu NotificationConsumer
            {
                'type': 'send_notification',
                'notification': {
                    'id': notification.id,
                    'type': notification.type,
                    'message': notification.message,
                    'board_id': notification.board_id,
                    'card_id': notification.card_id,
                    'is_read': notification.is_read,
                    'created_at': notification.created_at.isoformat(),
                    'sender': notification.sender.username if notification.sender else None
                }
            }
        )
    except Exception as e:
        print(f"Error enviando notificación WebSocket: {e}")

def _generar_mensaje_por_defecto(notification_type, sender):
    """Genera mensaje por defecto según el tipo"""
    mensajes = {
        'task_assigned': f"{sender.username} te asignó una tarea",
        'comment_added': f"{sender.username} comentó en una tarea tuya",
        'task_moved': f"{sender.username} movió una tarea",
        'mention': f"{sender.username} te mencionó",
        'member_added': f"{sender.username} te agregó a un tablero",
    }
    return mensajes.get(notification_type, "Tienes una nueva notificación")


def marcar_como_leida(notification_id, user):
    """Marca una notificación como leída"""
    try:
        notification = Notification.objects.get(id=notification_id, user=user)
        notification.is_read = True
        notification.save()
        return True
    except Notification.DoesNotExist:
        return False


def obtener_notificaciones_no_leidas(user):
    """Obtiene el conteo de notificaciones no leídas"""
    return Notification.objects.filter(user=user, is_read=False).count()