from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from boards.utils import get_accessible_board_ids
from notifications.models import Activity


def _serialize_activity(activity):
    return {
        'id': activity.id,
        'user': activity.user.username,
        'action': activity.action,
        'action_display': activity.get_action_display(),
        'description': activity.description,
        'board_id': activity.board_id,
        'card_id': activity.card_id,
        'created_at': activity.created_at.strftime('%d/%m/%Y %H:%M'),
        'time_ago': activity.created_at.isoformat(),
    }


@login_required
@require_GET
def activity_list(request):
    board_ids = get_accessible_board_ids(request.user)
    activities = Activity.objects.filter(board_id__in=board_ids).select_related('user')

    board_filter = request.GET.get('board')
    if board_filter and board_filter.isdigit():
        if int(board_filter) in board_ids:
            activities = activities.filter(board_id=int(board_filter))

    paginator = Paginator(activities, 30)
    page = paginator.get_page(request.GET.get('page', 1))

    from boards.models import Board
    boards = Board.objects.filter(id__in=board_ids).order_by('name')

    return render(request, 'activity/activity.html', {
        'activities': page,
        'boards': boards,
        'selected_board': board_filter,
    })


@login_required
@require_GET
def activity_api(request):
    board_ids = get_accessible_board_ids(request.user)
    limit = min(int(request.GET.get('limit', 20)), 50)
    activities = Activity.objects.filter(
        board_id__in=board_ids
    ).select_related('user')[:limit]

    return JsonResponse({
        'activities': [_serialize_activity(a) for a in activities],
    })
