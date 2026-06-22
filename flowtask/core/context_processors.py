def navigation(request):
    """Contexto global para navegación activa y estadísticas rápidas."""
    if not request.user.is_authenticated:
        return {}

    from boards.models import Card
    from boards.utils import get_user_boards
    from notifications.models import Activity, Notification

    boards = get_user_boards(request.user)
    board_ids = list(boards.values_list('id', flat=True))

    pending_tasks = Card.objects.filter(
        list__board_id__in=board_ids,
        is_completed=False,
    ).count()

    unread_notifications = Notification.objects.filter(
        user=request.user, is_read=False
    ).count()

    return {
        'nav_active': request.resolver_match.url_name if request.resolver_match else '',
        'user_board_count': boards.count(),
        'user_pending_tasks': pending_tasks,
        'user_unread_notifications': unread_notifications,
        'recent_activity_count': Activity.objects.filter(
            board_id__in=board_ids
        ).count() if board_ids else 0,
    }
