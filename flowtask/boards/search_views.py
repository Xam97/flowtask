from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.http import require_GET, require_http_methods
from django.views.decorators.csrf import csrf_protect

from boards.models import Board, Card, Label, CardLabel
from boards.utils import get_user_boards, get_accessible_board_ids, user_can_access_board


@login_required
@require_GET
def search_view(request):
    query = request.GET.get('q', '').strip()
    board_ids = get_accessible_board_ids(request.user)

    boards = []
    cards = []

    if query and len(query) >= 2:
        boards = Board.objects.filter(
            id__in=board_ids,
            is_archived=False,
        ).filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )[:10]

        cards = Card.objects.filter(
            list__board_id__in=board_ids,
        ).filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        ).select_related('list', 'list__board', 'assigned_to')[:20]

    return render(request, 'search/results.html', {
        'query': query,
        'boards': boards,
        'cards': cards,
    })


@login_required
@require_GET
def search_api(request):
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse({'boards': [], 'cards': []})

    board_ids = get_accessible_board_ids(request.user)

    boards = Board.objects.filter(
        id__in=board_ids, is_archived=False,
    ).filter(
        Q(name__icontains=query) | Q(description__icontains=query)
    )[:5]

    cards = Card.objects.filter(
        list__board_id__in=board_ids,
    ).filter(
        Q(title__icontains=query) | Q(description__icontains=query)
    ).select_related('list', 'list__board')[:8]

    return JsonResponse({
        'boards': [
            {'id': b.id, 'name': b.name, 'url': f'/boards/{b.id}/'}
            for b in boards
        ],
        'cards': [
            {
                'id': c.id,
                'title': c.title,
                'board_name': c.list.board.name,
                'list_name': c.list.name,
                'url': f'/boards/{c.list.board.id}/',
                'priority': c.priority,
            }
            for c in cards
        ],
    })


@login_required
def calendar_view(request):
    board_ids = get_accessible_board_ids(request.user)
    from datetime import datetime
    from django.utils import timezone

    month = request.GET.get('month')
    year = request.GET.get('year')

    now = timezone.now()
    try:
        current_month = int(month) if month else now.month
        current_year = int(year) if year else now.year
    except ValueError:
        current_month = now.month
        current_year = now.year

    cards = Card.objects.filter(
        list__board_id__in=board_ids,
        due_date__isnull=False,
        due_date__year=current_year,
        due_date__month=current_month,
    ).select_related('list', 'list__board', 'assigned_to').order_by('due_date')

    cards_by_day = {}
    for card in cards:
        day = card.due_date.day
        cards_by_day.setdefault(day, []).append(card)

    import calendar
    cal = calendar.Calendar(firstweekday=0)
    weeks = cal.monthdayscalendar(current_year, current_month)

    weeks_data = []
    for week in weeks:
        week_row = []
        for day in week:
            week_row.append({
                'day': day,
                'cards': cards_by_day.get(day, []) if day != 0 else [],
                'is_today': day == now.day and now.month == current_month and now.year == current_year,
            })
        weeks_data.append(week_row)

    prev_month = current_month - 1 if current_month > 1 else 12
    prev_year = current_year if current_month > 1 else current_year - 1
    next_month = current_month + 1 if current_month < 12 else 1
    next_year = current_year if current_month < 12 else current_year + 1

    month_names = [
        '', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
    ]

    overdue = Card.objects.filter(
        list__board_id__in=board_ids,
        due_date__lt=now,
        is_completed=False,
    ).select_related('list', 'list__board').order_by('due_date')[:10]

    return render(request, 'calendar/calendar.html', {
        'weeks_data': weeks_data,
        'current_month': current_month,
        'current_year': current_year,
        'month_name': month_names[current_month],
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'overdue_cards': overdue,
    })


@login_required
def labels_view(request):
    board_ids = get_accessible_board_ids(request.user)
    labels = Label.objects.filter(
        board_id__in=board_ids
    ).select_related('board').prefetch_related('cards')

    board_filter = request.GET.get('board')
    if board_filter and board_filter.isdigit() and int(board_filter) in board_ids:
        labels = labels.filter(board_id=int(board_filter))

    boards = get_user_boards(request.user).order_by('name')

    label_data = []
    for label in labels:
        label_data.append({
            'label': label,
            'card_count': label.cards.count(),
        })

    return render(request, 'labels/labels.html', {
        'label_data': label_data,
        'boards': boards,
        'selected_board': board_filter,
        'label_colors': Label.COLOR_CHOICES,
    })


@csrf_protect
@login_required
@require_http_methods(['POST'])
def create_label(request):
    board_id = request.POST.get('board_id')
    name = request.POST.get('name', '').strip()
    color = request.POST.get('color', '#579bfc')

    board = get_object_or_404(Board, pk=board_id, is_archived=False)
    if not user_can_access_board(request.user, board):
        messages.error(request, 'Sin permiso')
        return redirect('labels')

    if len(name) < 2:
        messages.error(request, 'El nombre debe tener al menos 2 caracteres')
        return redirect('labels')

    if Label.objects.filter(board=board, name=name).exists():
        messages.warning(request, f'La etiqueta "{name}" ya existe en este tablero')
        return redirect('labels')

    Label.objects.create(name=name, color=color, board=board)
    messages.success(request, f'Etiqueta "{name}" creada')
    return redirect('labels')


@csrf_protect
@login_required
@require_http_methods(['POST'])
def delete_label(request, label_id):
    label = get_object_or_404(Label, pk=label_id)
    if not user_can_access_board(request.user, label.board):
        messages.error(request, 'Sin permiso')
        return redirect('labels')

    name = label.name
    label.delete()
    messages.success(request, f'Etiqueta "{name}" eliminada')
    return redirect('labels')


@csrf_protect
@login_required
@require_http_methods(['POST'])
def toggle_card_label(request, card_id, label_id):
    card = get_object_or_404(Card, pk=card_id)
    label = get_object_or_404(Label, pk=label_id)

    if card.list.board_id != label.board_id:
        return JsonResponse({'success': False, 'error': 'Etiqueta no pertenece al tablero'}, status=400)

    if not user_can_access_board(request.user, card.list.board):
        return JsonResponse({'success': False, 'error': 'Sin permiso'}, status=403)

    existing = CardLabel.objects.filter(card=card, label=label).first()
    if existing:
        existing.delete()
        attached = False
    else:
        CardLabel.objects.create(card=card, label=label)
        attached = True

    return JsonResponse({'success': True, 'attached': attached})
