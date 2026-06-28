# Vistas completas para gestión de tableros, listas y tarjetas

from .forms import BoardForm, ListForm, CardForm
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.db import models
from .models import Board, List, Card, Membership
from .permissions import (
    user_can_access_board,
    user_has_permission,
    get_user_permissions,
    get_membership_permissions,
    GRANTABLE_FIELD_MAP,
)
from django.contrib.auth.models import User
from notifications.services import (
    notify_member_added, notify_task_assigned, log_activity,
    notify_card_moved, notify_card_deleted, notify_card_created,
    notify_card_edited, notify_list_created, notify_list_deleted,
    notify_list_edited, notify_board_created, notify_board_edited,
    notify_role_changed,
)
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .serializers import UserRegistrationSerializer


# ========== VISTAS DE TABLEROS ==========

@login_required
def board_list(request):
    """
    Lista todos los tableros del usuario (propios + colaboraciones)
    """
    # Boards donde el usuario es propietario
    owned_boards = request.user.owned_boards.filter(is_archived=False)
    
    # Boards donde el usuario es miembro PERO NO es propietario
    member_boards = request.user.boards.filter(is_archived=False).exclude(owner=request.user)
    
    context = {
        'owned_boards': owned_boards,
        'member_boards': member_boards,
    }
    return render(request, 'dashboard.html', context)


@login_required
@require_http_methods(["GET"])
def user_owned_boards_api(request):
    """API JSON con IDs de tableros propiedad del usuario."""
    owned_boards = request.user.owned_boards.filter(is_archived=False)
    owned_board_ids = list(owned_boards.values_list('id', flat=True))
    return JsonResponse({
        'success': True,
        'owned_board_ids': owned_board_ids,
    })


@login_required
def board_detail(request, pk):
    """
    Vista detallada de un tablero (vista Kanban)
    """
    board = get_object_or_404(Board, pk=pk, is_archived=False)
    
    if not user_can_access_board(request.user, board):
        messages.error(request, 'No tienes permiso para ver este tablero')
        return redirect('dashboard')
    
    # Obtener listas ordenadas por posición con sus tarjetas y conteo de comentarios
    lists = board.lists.all().prefetch_related(
        'cards__assigned_to',
        'cards__comments_card',
        'cards__labels',
    ).order_by('position')
    
    # Obtener miembros (evitando duplicados)
    members = list(board.members.all())
    if board.owner not in members:
        members.append(board.owner)
    
    memberships = list(
        Membership.objects.filter(board=board).select_related('user')
    )
    
    context = {
        'board': board,
        'lists': lists,
        'members': members,
        'memberships': memberships,
        'labels': board.labels.all(),
        'board_permissions': get_user_permissions(request.user, board),
        'is_owner': board.owner_id == request.user.id,
        'user_role': 'owner' if board.owner_id == request.user.id else (
            Membership.objects.filter(user=request.user, board=board).values_list('role', flat=True).first()
        ),
    }
    return render(request, 'boards/board_detail.html', context)


@csrf_protect
@login_required
@require_http_methods(["POST"])
def create_board(request):
    """
    Crea un nuevo tablero
    """
    name = request.POST.get('name') or request.POST.get('board_name')
    description = request.POST.get('description', '')
    
    if not name or len(name) < 3:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'El nombre debe tener al menos 3 caracteres'})
        messages.error(request, 'El nombre debe tener al menos 3 caracteres')
        return redirect('dashboard')
    
    board = Board.objects.create(
        name=name,
        description=description,
        owner=request.user
    )
    
    # Crear listas por defecto
    default_lists = ['Pendiente', 'En proceso', 'Terminado']
    for position, list_name in enumerate(default_lists):
        List.objects.create(
            name=list_name,
            board=board,
            position=(position + 1) * 10
        )

    log_activity(
        request.user, board.id, 'create_board',
        f'Creó el tablero "{board.name}"',
    )
    notify_board_created(board, request.user)

    # Verificar si es petición AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'board': {
                'id': board.id,
                'name': board.name,
                'description': board.description,
                'url': f'/boards/{board.id}/'
            }
        })
    
    # Para peticiones normales (formulario tradicional)
    messages.success(request, f'Tablero "{name}" creado exitosamente')
    return redirect('board_detail', pk=board.id)


@login_required
@require_http_methods(["POST"])
def delete_board(request, pk):
    """
    Elimina (archiva) un tablero
    """
    board = get_object_or_404(Board, pk=pk)
    
    if not user_has_permission(request.user, board, 'delete_board'):
        messages.error(request, 'Solo el propietario puede eliminar el tablero')
        return redirect('board_detail', pk=pk)
    
    board.is_archived = True
    board.save()
    messages.success(request, f'Tablero "{board.name}" archivado')
    return redirect('dashboard')


# ========== VISTAS DE LISTAS ==========

@csrf_protect
@login_required
@require_http_methods(["POST"])
def create_list(request, board_id):
    """
    Crea una nueva lista dentro de un tablero
    """
    board = get_object_or_404(Board, pk=board_id)
    
    if not user_has_permission(request.user, board, 'create_list'):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Sin permiso'}, status=403)
        messages.error(request, 'Sin permiso')
        return redirect('board_detail', pk=board_id)
    
    name = request.POST.get('name')
    if not name:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Nombre requerido'})
        messages.error(request, 'Nombre requerido')
        return redirect('board_detail', pk=board_id)
    
    max_position = board.lists.aggregate(models.Max('position'))['position__max'] or 0
    
    list_obj = List.objects.create(
        name=name,
        board=board,
        position=max_position + 10
    )

    log_activity(
        request.user, board.id, 'create_list',
        f'Creó la lista "{name}"',
    )
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'list': {
                'id': list_obj.id,
                'name': list_obj.name,
                'position': float(list_obj.position)
            }
        })
    
    return redirect('board_detail', pk=board_id)


@login_required
@require_http_methods(["POST"])
def delete_list(request, list_id):
    """
    Elimina una lista
    """
    list_obj = get_object_or_404(List, pk=list_id)
    board_id = list_obj.board.id
    
    if not user_has_permission(request.user, list_obj.board, 'delete_lists'):
        messages.error(request, 'Sin permiso para eliminar esta lista')
        return redirect('board_detail', pk=board_id)
    
    list_name = list_obj.name
    list_obj.delete()
    log_activity(
        request.user, board_id, 'delete_list',
        f'Eliminó la lista "{list_name}"',
    )
    messages.success(request, 'Lista eliminada')
    return redirect('board_detail', pk=board_id)


# ========== VISTAS DE TARJETAS ==========

@csrf_protect
@login_required
@require_http_methods(["POST"])
def create_card(request, list_id):
    """
    Crea una nueva tarjeta dentro de una lista
    """
    list_obj = get_object_or_404(List, pk=list_id)
    board = list_obj.board
    
    if not user_has_permission(request.user, board, 'create_card'):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Sin permiso'}, status=403)
        messages.error(request, 'Sin permiso')
        return redirect('board_detail', pk=board.id)
    
    title = request.POST.get('title')
    description = request.POST.get('description', '')
    assigned_to_id = request.POST.get('assigned_to')
    due_date = request.POST.get('due_date')
    
    if not title:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Título requerido'})
        messages.error(request, 'El título es requerido')
        return redirect('board_detail', pk=board.id)
    
    max_position = list_obj.cards.aggregate(models.Max('position'))['position__max'] or 0
    
    card = Card.objects.create(
        title=title,
        description=description,
        list=list_obj,
        created_by=request.user,
        position=max_position + 10,
        due_date=due_date if due_date else None
    )
    
    if assigned_to_id:
        try:
            assigned_user = User.objects.get(id=assigned_to_id)
            card.assigned_to = assigned_user
            card.save()
            notify_task_assigned(assigned_user, card, request.user)
        except User.DoesNotExist:
            pass

    log_activity(
        request.user, board.id, 'create_card',
        f'Creó la tarea "{title}" en "{list_obj.name}"',
        card_id=card.id,
    )
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'card': {
                'id': card.id,
                'title': card.title,
                'description': card.description,
                'created_by': card.created_by.username,
                'assigned_to': card.assigned_to.username if card.assigned_to else None,
                'position': float(card.position)
            }
        })
    
    messages.success(request, f'Tarea "{title}" creada')
    return redirect('board_detail', pk=board.id)


@login_required
@require_http_methods(["POST"])
def update_card_position(request):
    """
    Actualiza la posición de una tarjeta (para Drag & Drop)
    """
    import json
    data = json.loads(request.body)
    
    card_id = data.get('card_id')
    new_list_id = data.get('list_id')
    new_position = data.get('position')
    
    card = get_object_or_404(Card, pk=card_id)
    board_id = card.list.board.id
    board = card.list.board

    if not user_has_permission(request.user, board, 'move_card'):
        return JsonResponse({'success': False, 'error': 'Sin permiso'}, status=403)

    old_list_name = card.list.name
    old_list_id = card.list.id
    moved = False

    if new_list_id and new_list_id != card.list.id:
        new_list = get_object_or_404(List, pk=new_list_id)
        card.list = new_list
        moved = True

    if new_position is not None:
        card.position = float(new_position)

    card.save()

    if moved:
        log_activity(
            request.user, board_id, 'move_card',
            f'Movió "{card.title}" de "{old_list_name}" a "{card.list.name}"',
            card_id=card.id,
        )
        notify_card_moved(board, card, request.user, old_list_name)

    return JsonResponse({'success': True})


@login_required
@require_http_methods(["POST"])
def delete_card(request, card_id):
    """
    Elimina una tarjeta
    """
    card = get_object_or_404(Card, pk=card_id)
    board = card.list.board
    board_id = board.id
    
    if not user_has_permission(request.user, board, 'delete_cards'):
        messages.error(request, 'Sin permiso para eliminar esta tarea')
        return redirect('board_detail', pk=board_id)
    
    card_title = card.title
    card_id_val = card.id
    card.delete()
    log_activity(
        request.user, board_id, 'delete_card',
        f'Eliminó la tarea "{card_title}"',
    )
    notify_card_deleted(board, card_title, request.user, card_id_val)
    messages.success(request, 'Tarea eliminada')
    return redirect('board_detail', pk=board_id)


# ========== VISTAS DE MIEMBROS ==========

@login_required
@require_http_methods(["POST"])
def add_member(request, board_id):
    """
    Agrega un miembro al tablero
    """
    board = get_object_or_404(Board, pk=board_id)
    
    can_manage = user_has_permission(request.user, board, 'manage_members')
    can_invite = user_has_permission(request.user, board, 'invite_members')
    if not can_manage and not can_invite:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Sin permiso para invitar miembros'}, status=403)
        messages.error(request, 'Sin permiso')
        return redirect('board_detail', pk=board_id)
    
    username = request.POST.get('username')
    role = request.POST.get('role', 'member')
    
    if not can_manage and role != 'member' and role != 'viewer':
        role = 'member'
    
    # Permisos adicionales para miembros (solo el creador puede otorgarlos)
    extra_perms = {}
    if can_manage and role == 'member':
        for perm, field in GRANTABLE_FIELD_MAP.items():
            extra_perms[field] = request.POST.get(field) == 'on'
    
    try:
        user = User.objects.get(username=username)
        
        if user.id == board.owner_id:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'El creador ya pertenece al tablero'})
            messages.warning(request, 'El creador ya pertenece al tablero')
            return redirect('board_detail', pk=board_id)
        
        if Membership.objects.filter(user=user, board=board).exists():
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'El usuario ya es miembro'})
            messages.warning(request, f'{username} ya es miembro del tablero')
            return redirect('board_detail', pk=board_id)
        
        membership = Membership.objects.create(user=user, board=board, role=role, **extra_perms)
        notify_member_added(user, board, request.user)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'member': {
                    'id': user.id,
                    'username': user.username,
                    'role': role,
                    'membership_id': membership.id,
                    'permissions': get_membership_permissions(membership) if role == 'member' else {},
                }
            })
        
        messages.success(request, f'{username} agregado al tablero')
        
    except User.DoesNotExist:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Usuario no encontrado'})
        messages.error(request, f'Usuario "{username}" no encontrado')
    
    return redirect('board_detail', pk=board_id)


@login_required
@require_http_methods(["POST"])
def remove_member(request, membership_id):
    """
    Elimina un miembro del tablero
    """
    membership = get_object_or_404(Membership, pk=membership_id)
    board_id = membership.board.id
    
    if not user_has_permission(request.user, membership.board, 'manage_members'):
        messages.error(request, 'Sin permiso')
        return redirect('board_detail', pk=board_id)
    
    username = membership.user.username
    membership.delete()
    messages.success(request, f'{username} removido del tablero')
    return redirect('board_detail', pk=board_id)


@login_required
@require_http_methods(["GET"])
def board_members_api(request, board_id):
    """API JSON con miembros y permisos del tablero."""
    board = get_object_or_404(Board, pk=board_id, is_archived=False)
    if not user_can_access_board(request.user, board):
        return JsonResponse({'success': False, 'error': 'Sin permiso'}, status=403)

    memberships = Membership.objects.filter(board=board).select_related('user')
    members_data = [{
        'membership_id': m.id,
        'user_id': m.user.id,
        'username': m.user.username,
        'role': m.role,
        'role_display': m.get_role_display_name(),
        'permissions': get_membership_permissions(m) if m.role == 'member' else {},
        'joined_at': m.joined_at.strftime('%d/%m/%Y'),
    } for m in memberships]

    return JsonResponse({
        'success': True,
        'owner': {
            'user_id': board.owner.id,
            'username': board.owner.username,
            'role': 'owner',
        },
        'members': members_data,
        'can_manage': user_has_permission(request.user, board, 'manage_members'),
    })


@csrf_protect
@login_required
@require_http_methods(["POST"])
def update_member_permissions(request, membership_id):
    """Actualiza rol y permisos otorgables de un miembro (solo creador)."""
    membership = get_object_or_404(Membership, pk=membership_id)
    board = membership.board

    if not user_has_permission(request.user, board, 'manage_members'):
        return JsonResponse({'success': False, 'error': 'Sin permiso'}, status=403)

    new_role = request.POST.get('role', membership.role)
    if new_role in dict(Membership.ROLE_CHOICES):
        membership.role = new_role

    if membership.role == 'member':
        for perm, field in GRANTABLE_FIELD_MAP.items():
            setattr(membership, field, request.POST.get(field) == 'on')

    membership.save()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'membership': {
                'id': membership.id,
                'username': membership.user.username,
                'role': membership.role,
                'permissions': get_membership_permissions(membership),
            },
        })

    messages.success(request, f'Permisos de {membership.user.username} actualizados')
    return redirect('board_detail', pk=board.id)


# ========== EDICIÓN DE TABLEROS ==========

@login_required
@require_http_methods(["GET", "POST"])
def edit_board(request, pk):
    """
    Editar un tablero existente
    """
    board = get_object_or_404(Board, pk=pk, is_archived=False)
    
    if not user_has_permission(request.user, board, 'edit_board'):
        messages.error(request, 'No tienes permiso para editar este tablero')
        return redirect('board_detail', pk=pk)
    
    if request.method == 'POST':
        form = BoardForm(request.POST, instance=board)
        if form.is_valid():
            form.save()
            messages.success(request, f'Tablero "{board.name}" actualizado')
            return redirect('board_detail', pk=pk)
    else:
        form = BoardForm(instance=board)
    
    return render(request, 'boards/edit_board.html', {'form': form, 'board': board})


# ========== ELIMINACIÓN DEFINITIVA ==========

@login_required
@require_http_methods(["POST"])
def delete_board_permanent(request, pk):
    """
    Eliminar tablero permanentemente (no solo archivar)
    """
    board = get_object_or_404(Board, pk=pk)
    
    if not user_has_permission(request.user, board, 'delete_board'):
        messages.error(request, 'Solo el propietario puede eliminar el tablero')
        return redirect('board_detail', pk=pk)
    
    board_name = board.name
    board.delete()
    messages.success(request, f'Tablero "{board_name}" eliminado permanentemente')
    return redirect('dashboard')


# ========== EDICIÓN DE LISTAS ==========

@login_required
@require_http_methods(["GET", "POST"])
def edit_list(request, list_id):
    """
    Editar una lista existente
    """
    list_obj = get_object_or_404(List, pk=list_id)
    board = list_obj.board
    
    if not user_has_permission(request.user, board, 'edit_lists'):
        messages.error(request, 'Sin permiso')
        return redirect('board_detail', pk=board.id)
    
    if request.method == 'POST':
        form = ListForm(request.POST, instance=list_obj)
        if form.is_valid():
            form.save()
            messages.success(request, f'Lista actualizada')
            return redirect('board_detail', pk=board.id)
    else:
        form = ListForm(instance=list_obj)
    
    return render(request, 'boards/edit_list.html', {'form': form, 'list': list_obj, 'board': board})


# ========== EDICIÓN DE TARJETAS ==========

@login_required
@require_http_methods(["GET", "POST"])
def edit_card(request, card_id):
    """
    Editar una tarjeta existente
    """
    card = get_object_or_404(Card, pk=card_id)
    board = card.list.board
    
    if not user_can_access_board(request.user, board):
        messages.error(request, 'Sin permiso')
        return redirect('board_detail', pk=board.id)
    
    can_edit = user_has_permission(request.user, board, 'edit_card')
    if not can_edit:
        messages.error(request, 'No tienes permiso para editar tareas')
        return redirect('board_detail', pk=board.id)
    
    # Obtener miembros para el select de asignación
    members = list(board.members.all())
    if board.owner not in members:
        members.append(board.owner)
    
    if request.method == 'POST':
        old_assigned_id = card.assigned_to_id
        form = CardForm(request.POST, instance=card)
        if form.is_valid():
            form.save()
            log_activity(
                request.user, board.id, 'edit_card',
                f'Editó la tarea "{card.title}"',
                card_id=card.id,
            )
            if card.assigned_to_id and card.assigned_to_id != old_assigned_id:
                notify_task_assigned(card.assigned_to, card, request.user)
            messages.success(request, f'Tarea "{card.title}" actualizada')
            return redirect('board_detail', pk=board.id)
    else:
        form = CardForm(instance=card)
        # Personalizar el select de assigned_to con los miembros
        form.fields['assigned_to'].choices = [('', 'No asignar')] + [(u.id, u.username) for u in members]
    
    return render(request, 'boards/edit_card.html', {
        'form': form,
        'card': card,
        'board': board,
        'members': members,
        'board_labels': board.labels.all(),
        'card_label_ids': list(card.labels.values_list('id', flat=True)),
        'board_permissions': get_user_permissions(request.user, board),
    })


# ========== ACTUALIZAR POSICIÓN (AJAX) ==========

@login_required
@require_http_methods(["POST"])
def update_list_position(request):
    """
    Actualiza la posición de una lista (para ordenamiento)
    """
    import json
    data = json.loads(request.body)
    
    list_id = data.get('list_id')
    new_position = data.get('position')
    
    list_obj = get_object_or_404(List, pk=list_id)
    
    if not user_has_permission(request.user, list_obj.board, 'edit_lists'):
        return JsonResponse({'success': False, 'error': 'Sin permiso'}, status=403)
    
    if new_position is not None:
        list_obj.position = float(new_position)
        list_obj.save()
    
    return JsonResponse({'success': True})


# ========== REGISTRO DE USUARIOS (API REST) ==========

class RegisterView(generics.CreateAPIView):
    """Vista de registro con validaciones robustas"""
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserRegistrationSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': 'Usuario creado exitosamente',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)