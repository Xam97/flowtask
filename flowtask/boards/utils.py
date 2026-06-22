# boards/utils.py
from django.db.models import Q
from .models import Board

def get_user_boards(user):
    """
    Retorna el QuerySet de tableros no archivados donde el usuario 
    es el dueño o es un miembro invitado.
    """
    if not user.is_authenticated:
        return Board.objects.none()
    
    # Filtra tableros que NO estén archivados Y (sea dueño O sea miembro)
    return Board.objects.filter(
        is_archived=False
    ).filter(
        Q(owner=user) | Q(members=user)
    ).distinct()


def user_can_access_board(user, board):
    """
    Valida si un usuario específico tiene permisos para ver un tablero.
    """
    if board.is_archived:
        return False
    return board.owner_id == user.id or board.members.filter(id=user.id).exists()


def get_accessible_board_ids(user):
    """
    Retorna una lista plana de IDs de los tableros accesibles por el usuario.
    """
    return list(get_user_boards(user).values_list('id', flat=True))