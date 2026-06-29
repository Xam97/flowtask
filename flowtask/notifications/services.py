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


def _get_board_member_users(board, exclude_user=None):
    """Usuarios del tablero (miembros + owner), excluyendo opcionalmente uno."""
    user_ids = set(board.members.values_list('id', flat=True))
    user_ids.add(board.owner_id)
    if exclude_user:
        user_ids.discard(exclude_user.id)
    return User.objects.filter(id__in=user_ids)


def notify_card_moved(board, card, moved_by, old_list_name):
    """Notifica a miembros del tablero cuando una tarjeta se mueve."""
    recipients = _get_board_member_users(board, exclude_user=moved_by)
    for user in recipients:
        create_notification(
            user=user,
            notif_type='card_moved',
            title='Tarjeta movida',
            message=(
                f'{moved_by.username} movió "{card.title}" '
                f'de "{old_list_name}" a "{card.list.name}" en "{board.name}"'
            ),
            board_id=board.id,
            card_id=card.id,
        )


def notify_card_deleted(board, card_title, deleted_by, card_id=None):
    """Notifica a miembros del tablero cuando se elimina una tarjeta."""
    recipients = _get_board_member_users(board, exclude_user=deleted_by)
    for user in recipients:
        create_notification(
            user=user,
            notif_type='card_deleted',
            title='Tarjeta eliminada',
            message=f'{deleted_by.username} eliminó la tarea "{card_title}" en "{board.name}"',
            board_id=board.id,
            card_id=card_id,
        )


def notify_card_created(board, card, created_by):
    """Notifica a miembros del tablero cuando se crea una tarjeta."""
    recipients = _get_board_member_users(board, exclude_user=created_by)
    for user in recipients:
        create_notification(
            user=user,
            notif_type='card_created',
            title='Nueva tarea creada',
            message=f'{created_by.username} creó la tarea "{card.title}" en "{board.name}"',
            board_id=board.id,
            card_id=card.id,
        )


def notify_card_edited(board, card, edited_by):
    """Notifica a miembros del tablero cuando se edita una tarjeta."""
    recipients = _get_board_member_users(board, exclude_user=edited_by)
    for user in recipients:
        create_notification(
            user=user,
            notif_type='card_edited',
            title='Tarea editada',
            message=f'{edited_by.username} editó la tarea "{card.title}" en "{board.name}"',
            board_id=board.id,
            card_id=card.id,
        )


def notify_list_created(board, list_obj, created_by):
    """Notifica a miembros del tablero cuando se crea una lista."""
    recipients = _get_board_member_users(board, exclude_user=created_by)
    for user in recipients:
        create_notification(
            user=user,
            notif_type='list_created',
            title='Nueva lista creada',
            message=f'{created_by.username} creó la lista "{list_obj.name}" en "{board.name}"',
            board_id=board.id,
        )


def notify_list_deleted(board, list_name, deleted_by):
    """Notifica a miembros del tablero cuando se elimina una lista."""
    recipients = _get_board_member_users(board, exclude_user=deleted_by)
    for user in recipients:
        create_notification(
            user=user,
            notif_type='list_deleted',
            title='Lista eliminada',
            message=f'{deleted_by.username} eliminó la lista "{list_name}" en "{board.name}"',
            board_id=board.id,
        )


def notify_list_edited(board, list_obj, edited_by):
    """Notifica a miembros del tablero cuando se edita una lista."""
    recipients = _get_board_member_users(board, exclude_user=edited_by)
    for user in recipients:
        create_notification(
            user=user,
            notif_type='list_edited',
            title='Lista editada',
            message=f'{edited_by.username} editó la lista "{list_obj.name}" en "{board.name}"',
            board_id=board.id,
        )


def notify_board_created(board, created_by):
    """Notifica al creador que se creó el tablero (confirmación)."""
    create_notification(
        user=created_by,
        notif_type='board_created',
        title='Tablero creado',
        message=f'Creaste el tablero "{board.name}" exitosamente',
        board_id=board.id,
    )


def notify_board_edited(board, edited_by):
    """Notifica a miembros del tablero cuando se edita."""
    recipients = _get_board_member_users(board, exclude_user=edited_by)
    for user in recipients:
        create_notification(
            user=user,
            notif_type='board_edited',
            title='Tablero editado',
            message=f'{edited_by.username} editó el tablero "{board.name}"',
            board_id=board.id,
        )


def notify_role_changed(board, member_user, new_role, changed_by):
    """Notifica al miembro cuando cambia su rol."""
    if member_user.id == changed_by.id:
        return
    create_notification(
        user=member_user,
        notif_type='role_changed',
        title='Rol cambiado',
        message=f'{changed_by.username} cambió tu rol a "{new_role}" en "{board.name}"',
        board_id=board.id,
    )
    log_activity(
        changed_by,
        board.id,
        'change_role',
        f'Cambió el rol de {member_user.username} a "{new_role}"',
    )
