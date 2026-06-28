from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods

from .models import Notification
from .services import _notification_payload


def _serialize_notification(notification):
    return _notification_payload(notification)


@login_required
@require_http_methods(["GET"])
def notification_list(request):
    qs = Notification.objects.filter(user=request.user)

    notif_type = request.GET.get('type')
    if notif_type:
        qs = qs.filter(type=notif_type)

    is_read = request.GET.get('is_read')
    if is_read == 'true':
        qs = qs.filter(is_read=True)
    elif is_read == 'false':
        qs = qs.filter(is_read=False)

    board_id = request.GET.get('board_id')
    if board_id and board_id.isdigit():
        qs = qs.filter(board_id=int(board_id))

    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()

    try:
        limit = min(int(request.GET.get('limit', 30)), 100)
    except ValueError:
        limit = 30

    try:
        page = max(int(request.GET.get('page', 1)), 1)
    except ValueError:
        page = 1

    offset = (page - 1) * limit
    total = qs.count()
    notifications = qs[offset:offset + limit]

    return JsonResponse({
        'success': True,
        'unread_count': unread_count,
        'total': total,
        'page': page,
        'limit': limit,
        'has_more': offset + limit < total,
        'notifications': [_serialize_notification(n) for n in notifications],
    })


@login_required
@require_http_methods(["GET"])
def notification_detail(request, notification_id):
    notification = get_object_or_404(Notification, pk=notification_id, user=request.user)
    return JsonResponse({
        'success': True,
        'notification': _serialize_notification(notification),
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


@login_required
@require_http_methods(["DELETE", "POST"])
def delete_notification(request, notification_id):
    notification = get_object_or_404(Notification, pk=notification_id, user=request.user)
    notification.delete()
    unread = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'success': True, 'unread_count': unread})


@login_required
@require_http_methods(["POST"])
def delete_all_read(request):
    deleted, _ = Notification.objects.filter(user=request.user, is_read=True).delete()
    unread = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'success': True, 'deleted_count': deleted, 'unread_count': unread})
