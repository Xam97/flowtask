from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth.models import User

from .models import Notification, Activity


def _notification_payload(notification):
    return {
        'id': notification.id,
        'type': notification.type,
        'title': notification.title,
        'message': notification.message,
        'board_id': notification.board_id,
        'card_id': notification.card_id,
        'is_read': notification.is_read,
        'created_at': notification.created_at.strftime('%d/%m/%Y %H:%M'),
    }


def push_notification_ws(user_id, notification):
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return
    async_to_sync(channel_layer.group_send)(
        f'notifications_{user_id}',
        {
            'type': 'send_notification',
            'data': _notification_payload(notification),
        },
    )


def create_notification(user, notif_type, title, message, board_id=None, card_id=None, push=True):
    notification = Notification.objects.create(
        user=user,
        type=notif_type,
        title=title,
        message=message,
        board_id=board_id,
        card_id=card_id,
    )
    if push:
        push_notification_ws(user.id, notification)
    return notification


def log_activity(user, board_id, action, description, card_id=None):
    Activity.objects.create(
        user=user,
        board_id=board_id,
        card_id=card_id,
        action=action,
        description=description,
    )


def notify_member_added(user, board, added_by):
    if user.id == added_by.id:
        return
    create_notification(
        user=user,
        notif_type='member_added',
        title='Nuevo tablero',
        message=f'{added_by.username} te agregó al tablero "{board.name}"',
        board_id=board.id,
    )
    log_activity(
        added_by,
        board.id,
        'add_member',
        f'Agregó a {user.username} al tablero "{board.name}"',
    )


def notify_task_assigned(user, card, assigned_by):
    if user.id == assigned_by.id:
        return
    board = card.list.board
    create_notification(
        user=user,
        notif_type='card_assigned',
        title='Nueva tarea asignada',
        message=f'{assigned_by.username} te asignó la tarea "{card.title}" en "{board.name}"',
        board_id=board.id,
        card_id=card.id,
    )
    log_activity(
        assigned_by,
        board.id,
        'edit_card',
        f'Asignó la tarea "{card.title}" a {user.username}',
        card_id=card.id,
    )


def notify_new_comment(recipients, card, commenter, comment_content):
    board = card.list.board
    preview = comment_content[:80] + ('...' if len(comment_content) > 80 else '')
    notified_ids = set()

    for user in recipients:
        if user.id == commenter.id or user.id in notified_ids:
            continue
        notified_ids.add(user.id)
        create_notification(
            user=user,
            notif_type='new_comment',
            title='Nuevo comentario',
            message=f'{commenter.username} comentó en "{card.title}": {preview}',
            board_id=board.id,
            card_id=card.id,
        )

    log_activity(
        commenter,
        board.id,
        'add_comment',
        f'Comentó en la tarea "{card.title}"',
        card_id=card.id,
    )


def get_comment_notification_recipients(card):
    recipients = []
    if card.assigned_to:
        recipients.append(card.assigned_to)
    if card.created_by and card.created_by != card.assigned_to:
        recipients.append(card.created_by)
    return recipients


def broadcast_board_event(board_id, event_type, data):
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return
    async_to_sync(channel_layer.group_send)(
        f'board_{board_id}',
        {'type': event_type, 'data': data},
    )
