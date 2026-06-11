from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods

from .models import Notification


@login_required
@require_http_methods(["GET"])
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user)[:30]
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({
        'success': True,
        'unread_count': unread_count,
        'notifications': [
            {
                'id': n.id,
                'type': n.type,
                'title': n.title,
                'message': n.message,
                'board_id': n.board_id,
                'card_id': n.card_id,
                'is_read': n.is_read,
                'created_at': n.created_at.strftime('%d/%m/%Y %H:%M'),
            }
            for n in notifications
        ],
    })


@login_required
@require_http_methods(["GET"])
def unread_count(request):
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'success': True, 'unread_count': count})


@login_required
@require_http_methods(["POST"])
def mark_read(request, notification_id=None):
    if notification_id:
        notification = get_object_or_404(Notification, pk=notification_id, user=request.user)
        notification.is_read = True
        notification.save(update_fields=['is_read'])
    else:
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    unread = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'success': True, 'unread_count': unread})


@login_required
@require_http_methods(["POST"])
def mark_all_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'success': True, 'unread_count': 0})
