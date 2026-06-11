from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect

from boards.models import Card
from notifications.services import (
    broadcast_board_event,
    get_comment_notification_recipients,
    notify_new_comment,
)
from .models import Comment


def _user_has_board_access(user, board):
    return board.owner_id == user.id or board.members.filter(id=user.id).exists()


def _serialize_comment(comment):
    return {
        'id': comment.id,
        'card_id': comment.card_id,
        'user': comment.user.username,
        'user_id': comment.user_id,
        'content': comment.content,
        'created_at': comment.created_at.strftime('%d/%m/%Y %H:%M'),
        'is_own': False,
    }


@login_required
@require_http_methods(["GET"])
def list_comments(request, card_id):
    card = get_object_or_404(Card, pk=card_id)
    board = card.list.board

    if not _user_has_board_access(request.user, board):
        return JsonResponse({'success': False, 'error': 'Sin permiso'}, status=403)

    comments = []
    can_comment = bool(card.assigned_to)
    if can_comment:
        comments = [
            {**_serialize_comment(c), 'is_own': c.user_id == request.user.id}
            for c in card.comments_card.select_related('user').all()
        ]

    return JsonResponse({
        'success': True,
        'can_comment': can_comment,
        'card': {
            'id': card.id,
            'title': card.title,
            'description': card.description,
            'priority': card.priority,
            'assigned_to': card.assigned_to.username if card.assigned_to else None,
            'created_by': card.created_by.username,
            'list_name': card.list.name,
            'board_id': board.id,
            'board_name': board.name,
        },
        'comments': comments,
    })


@csrf_protect
@login_required
@require_http_methods(["POST"])
def add_comment(request, card_id):
    card = get_object_or_404(Card, pk=card_id)
    board = card.list.board

    if not _user_has_board_access(request.user, board):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Sin permiso'}, status=403)
        messages.error(request, 'Sin permiso')
        return JsonResponse({'success': False, 'error': 'Sin permiso'}, status=403)

    if not card.assigned_to:
        error_msg = 'Solo puedes comentar en tareas que tengan alguien asignado'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': error_msg}, status=400)
        messages.error(request, error_msg)
        return JsonResponse({'success': False, 'error': error_msg}, status=400)

    content = request.POST.get('content', '').strip()
    if not content:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'El comentario no puede estar vacío'})
        messages.error(request, 'El comentario no puede estar vacío')
        return JsonResponse({'success': False, 'error': 'El comentario no puede estar vacío'})

    comment = Comment.objects.create(
        card=card,
        user=request.user,
        content=content,
    )

    comment_data = {
        'comment_id': comment.id,
        'card_id': card.id,
        'user': comment.user.username,
        'user_id': comment.user_id,
        'comment': comment.content,
        'created_at': comment.created_at.strftime('%d/%m/%Y %H:%M'),
    }

    broadcast_board_event(board.id, 'new_comment', comment_data)
    notify_new_comment(
        get_comment_notification_recipients(card),
        card,
        request.user,
        content,
    )

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'comment': {**comment_data, 'is_own': True},
        })

    messages.success(request, 'Comentario agregado')
    return JsonResponse({'success': True, 'comment': comment_data})


@login_required
@require_http_methods(["POST"])
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    board = comment.card.list.board
    board_id = board.id

    if comment.user != request.user and board.owner != request.user:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Sin permiso'}, status=403)
        messages.error(request, 'No tienes permiso para eliminar este comentario')
        return JsonResponse({'success': False, 'error': 'Sin permiso'}, status=403)

    card_id = comment.card_id
    comment.delete()

    broadcast_board_event(board_id, 'comment_deleted', {
        'comment_id': comment_id,
        'card_id': card_id,
    })

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})

    messages.success(request, 'Comentario eliminado')
    return JsonResponse({'success': True})
