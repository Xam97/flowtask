from django.db.models import Q

from .models import Board
from .permissions import user_can_access_board as _user_can_access_board


def get_user_boards(user):
    """Tableros accesibles por el usuario (propios + membresía), no archivados."""
    return Board.objects.filter(is_archived=False).filter(
        Q(owner=user) | Q(members=user)
    ).distinct()


def user_can_access_board(user, board):
    if board.is_archived:
        return False
    return _user_can_access_board(user, board)


def get_accessible_board_ids(user):
    return list(get_user_boards(user).values_list('id', flat=True))
