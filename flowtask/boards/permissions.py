"""Capa centralizada de roles y permisos por tablero."""

from .models import Membership

# Permisos base que los miembros tienen por defecto (sin flags adicionales)
MEMBER_BASE_PERMISSIONS = frozenset({
    'view',
    'create_card',
    'edit_card',
    'move_card',
    'comment',
    'create_list',
})

# Permisos otorgables por el creador a miembros individuales
GRANTABLE_PERMISSIONS = frozenset({
    'manage_labels',
    'delete_cards',
    'edit_lists',
    'invite_members',
})

# Todos los permisos posibles
ALL_PERMISSIONS = MEMBER_BASE_PERMISSIONS | GRANTABLE_PERMISSIONS | frozenset({
    'edit_board',
    'delete_board',
    'delete_lists',
    'manage_members',
})

GRANTABLE_FIELD_MAP = {
    'manage_labels': 'can_manage_labels',
    'delete_cards': 'can_delete_cards',
    'edit_lists': 'can_edit_lists',
    'invite_members': 'can_invite',
}


def get_membership(user, board):
    """Retorna la membresía del usuario en el tablero, o None si es owner/externo."""
    if not user or not user.is_authenticated:
        return None
    return Membership.objects.filter(user=user, board=board).first()


def get_board_role(user, board):
    """Retorna 'owner', 'admin', 'member', 'viewer' o None."""
    if not user or not user.is_authenticated:
        return None
    if board.owner_id == user.id:
        return 'owner'
    membership = get_membership(user, board)
    return membership.role if membership else None


def user_can_access_board(user, board):
    """Acceso de lectura al tablero."""
    return get_board_role(user, board) is not None


def user_has_permission(user, board, permission):
    """Verifica si el usuario tiene un permiso específico en el tablero."""
    role = get_board_role(user, board)
    if role is None:
        return False

    if role == 'owner':
        return True

    if role == 'viewer':
        return permission == 'view'

    if role == 'admin':
        admin_perms = MEMBER_BASE_PERMISSIONS | GRANTABLE_PERMISSIONS | frozenset({
            'edit_board', 'edit_lists', 'manage_labels', 'delete_cards',
        })
        return permission in admin_perms

    # role == 'member'
    if permission in MEMBER_BASE_PERMISSIONS:
        return True

    if permission in GRANTABLE_PERMISSIONS:
        membership = get_membership(user, board)
        if not membership:
            return False
        field = GRANTABLE_FIELD_MAP.get(permission)
        return field and getattr(membership, field, False)

    return False


def get_user_permissions(user, board):
    """Retorna dict {permiso: bool} para uso en templates."""
    return {perm: user_has_permission(user, board, perm) for perm in ALL_PERMISSIONS}


def get_membership_permissions(membership):
    """Retorna los permisos otorgables actuales de una membresía."""
    return {
        perm: getattr(membership, field, False)
        for perm, field in GRANTABLE_FIELD_MAP.items()
    }
