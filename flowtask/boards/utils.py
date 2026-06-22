# boards/utils.py
from .models import Board

def get_accessible_board_ids(user):
    # Aquí va la lógica original de tu proyecto. Generalmente es algo como:
    # Retornar los IDs de los tableros de los cuales el usuario es miembro o dueño.
    return list(Board.objects.filter(user=user).values_list('id', flat=True))


def user_can_access_board(user, board):
    if board.is_archived:
        return False
    return board.owner_id == user.id or board.members.filter(id=user.id).exists()


def get_accessible_board_ids(user):
    return list(get_user_boards(user).values_list('id', flat=True))