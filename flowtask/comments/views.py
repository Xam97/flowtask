from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from boards.models import Card
from .models import Comment


@csrf_protect
@login_required
@require_http_methods(["POST"])
def add_comment(request, card_id):
    """
    Agrega un comentario a una tarjeta
    """
    card = get_object_or_404(Card, pk=card_id)
    content = request.POST.get('content', '').strip()
    
    if not content:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'El comentario no puede estar vacío'})
        messages.error(request, 'El comentario no puede estar vacío')
        return redirect('board_detail', pk=card.list.board.id)
    
    comment = Comment.objects.create(
        card=card,
        user=request.user,
        content=content
    )
    
    # Si es AJAX, devolver JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'comment': {
                'id': comment.id,
                'user': comment.user.username,
                'content': comment.content,
                'created_at': comment.created_at.strftime('%d/%m/%Y %H:%M')
            }
        })
    
    messages.success(request, 'Comentario agregado')
    return redirect('board_detail', pk=card.list.board.id)


@login_required
@require_http_methods(["POST"])
def delete_comment(request, comment_id):
    """
    Elimina un comentario (solo el autor o admin)
    """
    comment = get_object_or_404(Comment, pk=comment_id)
    board_id = comment.card.list.board.id
    
    # Solo el autor o el owner del tablero pueden eliminar
    if comment.user != request.user and comment.card.list.board.owner != request.user:
        messages.error(request, 'No tienes permiso para eliminar este comentario')
        return redirect('board_detail', pk=board_id)
    
    comment.delete()
    messages.success(request, 'Comentario eliminado')
    return redirect('board_detail', pk=board_id)