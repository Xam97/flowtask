# boards/admin.py
# Configuración del panel administrativo
# Optimizado para gestión de tableros, listas y tarjetas

from django.contrib import admin
from .models import Board, Membership, List, Card


# ========== BOARD ADMIN ==========
@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'is_archived', 'created_at', 'get_member_count']
    list_filter = ['is_archived', 'created_at', 'owner']
    search_fields = ['name', 'description', 'owner__username']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_member_count(self, obj):
        return obj.members.count()
    get_member_count.short_description = "Miembros"


# ========== MEMBERSHIP ADMIN ==========
@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'board', 'role', 'joined_at']
    list_filter = ['role', 'joined_at']
    search_fields = ['user__username', 'board__name']


# ========== LIST ADMIN ==========
@admin.register(List)
class ListAdmin(admin.ModelAdmin):
    list_display = ['name', 'board', 'position', 'created_at']
    list_filter = ['board', 'created_at']
    search_fields = ['name', 'board__name']
    readonly_fields = ['created_at', 'updated_at']


# ========== CARD ADMIN ==========
@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ['title', 'list', 'assigned_to', 'priority', 'is_completed', 'due_date']
    list_filter = ['priority', 'is_completed', 'list__board', 'created_at']
    search_fields = ['title', 'description', 'assigned_to__username']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'board', 'created_at']
    list_filter = ['board']
    search_fields = ['name']


@admin.register(CardLabel)
class CardLabelAdmin(admin.ModelAdmin):
    list_display = ['card', 'label', 'added_at']