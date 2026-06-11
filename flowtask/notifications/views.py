# notifications/views.py
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Notification

@login_required
def get_notifications(request):
    """
    Obtiene las notificaciones del usuario autenticado
    """
    limit = int(request.GET.get('limit', 10))
    
    # 🔴 CAMBIO: recipient → user
    notifications = Notification.objects.filter(
        user=request.user  # 👈 Cambiado de 'recipient' a 'user'
    ).order_by('-created_at')[:limit]
    
    # 🔴 CAMBIO: recipient → user
    unread_count = Notification.objects.filter(
        user=request.user,  # 👈 Cambiado de 'recipient' a 'user'
        is_read=False
    ).count()
    
    data = {
        'unread_count': unread_count,
        'notifications': [
            {
                'id': n.id,
                'type': n.type,  # 👈 Asegúrate que tu modelo tiene 'type'
                'message': n.message,
                'board_id': n.board_id,
                'card_id': n.card_id,
                'is_read': n.is_read,
                'created_at': n.created_at.isoformat(),
                'sender': n.sender.username if n.sender else None
            }
            for n in notifications
        ]
    }
    return JsonResponse(data)


@login_required
@require_http_methods(["POST"])
def mark_as_read(request, notification_id):
    """
    Marca una notificación como leída
    """
    # 🔴 CAMBIO: recipient → user
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'success': True})


@login_required
@require_http_methods(["POST"])
def mark_all_as_read(request):
    """
    Marca todas las notificaciones del usuario como leídas
    """
    # 🔴 CAMBIO: recipient → user
    count = Notification.objects.filter(
        user=request.user,  # 👈 Cambiado de 'recipient' a 'user'
        is_read=False
    ).update(is_read=True)
    
    return JsonResponse({'success': True, 'marked_count': count})