from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.http import require_GET, require_http_methods
from django.views.decorators.csrf import csrf_protect
import json
import re

from boards.models import Board, Card, Label, CardLabel
from boards.utils import get_user_boards, get_accessible_board_ids, user_can_access_board
from boards.permissions import user_has_permission, get_user_permissions

HEX_COLOR_RE = re.compile(r'^#[0-9A-Fa-f]{6}$')


def _validate_color(color):
    if HEX_COLOR_RE.match(color):
        return color
    preset = dict(Label.COLOR_CHOICES)
    return color if color in preset else '#579bfc'


def _serialize_label(label):
    return {
        'id': label.id,
        'name': label.name,
        'color': label.color,
        'board_id': label.board_id,
        'board_name': label.board.name,
        'card_count': label.cards.count(),
    }


@login_required
@require_GET
def search_view(request):
    query = request.GET.get('q', '').strip()
    board_ids = get_accessible_board_ids(request.user)

    boards = []
    cards = []
    users_list = []

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

        
        raw_users = User.objects.filter(
            (Q(username__icontains=query) | 
             Q(first_name__icontains=query) | 
             Q(last_name__icontains=query) | 
             Q(email__icontains=query)) &
            ~Q(id=request.user.id)
        )[:10]

        for u in raw_users:
            u.contact_status = 'none'
            users_list.append(u)

    return render(request, 'search/results.html', {
        'query': query,
        'boards': boards,
        'cards': cards,
        'users': users_list,
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
    perms_by_board = {b.id: get_user_permissions(request.user, b) for b in boards}

    label_data = []
    for label in labels:
        label_data.append({
            'label': label,
            'card_count': label.cards.count(),
            'can_manage': user_has_permission(request.user, label.board, 'manage_labels'),
        })

    return render(request, 'labels/labels.html', {
        'label_data': label_data,
        'boards': boards,
        'selected_board': board_filter,
        'label_colors': Label.COLOR_CHOICES,
        'label_permissions_json': json.dumps({
            str(bid): perms for bid, perms in perms_by_board.items()
        }),
    })


@login_required
def panel_view(request):
    """Panel de métricas y reportes en tiempo real"""
    from django.db.models import Count, Q, Avg
    from django.utils import timezone
    from datetime import timedelta
    
    board_ids = get_accessible_board_ids(request.user)
    boards = get_user_boards(request.user).order_by('name')
    
    selected_board_id = request.GET.get('board')
    if selected_board_id and selected_board_id.isdigit() and int(selected_board_id) in board_ids:
        selected_board_id = int(selected_board_id)
    elif boards.exists():
        selected_board_id = boards.first().id
    else:
        selected_board_id = None
    
    metrics = {}
    board_cards = []
    
    if selected_board_id:
        board = get_object_or_404(Board, pk=selected_board_id, is_archived=False)
        
        # Métricas generales
        total_cards = Card.objects.filter(list__board=board).count()
        completed_cards = Card.objects.filter(list__board=board, is_completed=True).count()
        pending_cards = total_cards - completed_cards
        
        # Tarjetas por prioridad
        priority_stats = Card.objects.filter(list__board=board).values('priority').annotate(
            count=Count('id')
        ).order_by('priority')
        
        # Tarjetas por lista
        list_stats = []
        for lst in board.lists.all():
            list_stats.append({
                'name': lst.name,
                'total': lst.cards.count(),
                'completed': lst.cards.filter(is_completed=True).count(),
            })
        
        # Tarjetas vencidas y próximas a vencer
        now = timezone.now()
        overdue = Card.objects.filter(
            list__board=board,
            due_date__lt=now,
            is_completed=False
        ).count()
        
        due_soon = Card.objects.filter(
            list__board=board,
            due_date__gte=now,
            due_date__lte=now + timedelta(days=7),
            is_completed=False
        ).count()
        
        # Tarjetas asignadas vs sin asignar
        assigned = Card.objects.filter(list__board=board, assigned_to__isnull=False).count()
        unassigned = total_cards - assigned
        
        # Actividad reciente (últimos 7 días)
        week_ago = now - timedelta(days=7)
        recent_activity = Card.objects.filter(
            list__board=board,
            created_at__gte=week_ago
        ).count()
        
        metrics = {
            'total_cards': total_cards,
            'completed_cards': completed_cards,
            'pending_cards': pending_cards,
            'completion_rate': round((completed_cards / total_cards * 100) if total_cards > 0 else 0, 1),
            'overdue': overdue,
            'due_soon': due_soon,
            'assigned': assigned,
            'unassigned': unassigned,
            'recent_activity': recent_activity,
            'priority_stats': list(priority_stats),
            'list_stats': list_stats,
        }
        
        # Tarjetas recientes para mostrar
        board_cards = Card.objects.filter(
            list__board=board
        ).select_related('list', 'assigned_to').order_by('-created_at')[:10]
    
    return render(request, 'panel/panel.html', {
        'boards': boards,
        'selected_board': selected_board_id,
        'metrics': metrics,
        'board_cards': board_cards,
    })


@login_required
@require_GET
def labels_api(request):
    """API JSON para listar etiquetas de tableros accesibles."""
    board_ids = get_accessible_board_ids(request.user)
    board_id = request.GET.get('board_id')

    labels = Label.objects.filter(board_id__in=board_ids).select_related('board')
    if board_id and board_id.isdigit() and int(board_id) in board_ids:
        labels = labels.filter(board_id=int(board_id))

    return JsonResponse({
        'success': True,
        'labels': [_serialize_label(l) for l in labels],
    })


@csrf_protect
@login_required
@require_http_methods(['POST'])
def create_label(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if is_ajax:
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            data = request.POST
    else:
        data = request.POST

    board_id = data.get('board_id')
    name = (data.get('name') or '').strip()
    color = _validate_color(data.get('color', '#579bfc'))

    board = get_object_or_404(Board, pk=board_id, is_archived=False)
    if not user_has_permission(request.user, board, 'manage_labels'):
        if is_ajax:
            return JsonResponse({'success': False, 'error': 'Sin permiso'}, status=403)
        messages.error(request, 'Sin permiso')
        return redirect('labels')

    if len(name) < 2:
        if is_ajax:
            return JsonResponse({'success': False, 'error': 'El nombre debe tener al menos 2 caracteres'})
        messages.error(request, 'El nombre debe tener al menos 2 caracteres')
        return redirect('labels')

    if Label.objects.filter(board=board, name=name).exists():
        if is_ajax:
            return JsonResponse({'success': False, 'error': f'La etiqueta "{name}" ya existe'})
        messages.warning(request, f'La etiqueta "{name}" ya existe en este tablero')
        return redirect('labels')

    label = Label.objects.create(name=name, color=color, board=board)

    if is_ajax:
        return JsonResponse({'success': True, 'label': _serialize_label(label)})

    messages.success(request, f'Etiqueta "{name}" creada')
    return redirect('labels')


@csrf_protect
@login_required
@require_http_methods(['POST', 'PUT', 'PATCH'])
def update_label(request, label_id):
    label = get_object_or_404(Label, pk=label_id)
    board = label.board

    if not user_has_permission(request.user, board, 'manage_labels'):
        return JsonResponse({'success': False, 'error': 'Sin permiso'}, status=403)

    try:
        data = json.loads(request.body) if request.body else request.POST
    except json.JSONDecodeError:
        data = request.POST

    name = (data.get('name') or label.name).strip()
    color = _validate_color(data.get('color', label.color))

    if len(name) < 2:
        return JsonResponse({'success': False, 'error': 'El nombre debe tener al menos 2 caracteres'})

    if Label.objects.filter(board=board, name=name).exclude(pk=label.id).exists():
        return JsonResponse({'success': False, 'error': f'La etiqueta "{name}" ya existe'})

    label.name = name
    label.color = color
    label.save()

    return JsonResponse({'success': True, 'label': _serialize_label(label)})


@csrf_protect
@login_required
@require_http_methods(['POST'])
def delete_label(request, label_id):
    label = get_object_or_404(Label, pk=label_id)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if not user_has_permission(request.user, label.board, 'manage_labels'):
        if is_ajax:
            return JsonResponse({'success': False, 'error': 'Sin permiso'}, status=403)
        messages.error(request, 'Sin permiso')
        return redirect('labels')

    name = label.name
    label.delete()

    if is_ajax:
        return JsonResponse({'success': True, 'message': f'Etiqueta "{name}" eliminada'})

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

    if not user_has_permission(request.user, card.list.board, 'manage_labels'):
        return JsonResponse({'success': False, 'error': 'Sin permiso para gestionar etiquetas'}, status=403)

    existing = CardLabel.objects.filter(card=card, label=label).first()
    if existing:
        existing.delete()
        attached = False
    else:
        CardLabel.objects.create(card=card, label=label)
        attached = True

    return JsonResponse({'success': True, 'attached': attached})
