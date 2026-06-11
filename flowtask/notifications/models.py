# notifications/models.py

from django.db import models
from django.contrib.auth.models import User


class Notification(models.Model):
    
    NOTIFICATION_TYPES = [
        ('card_moved', 'Tarjeta movida'),
        ('card_assigned', 'Tarea asignada'),
        ('new_comment', 'Nuevo comentario'),
        ('member_added', 'Miembro agregado'),
        ('card_deleted', 'Tarjeta eliminada'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications_user')
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    board_id = models.IntegerField(null=True, blank=True)
    card_id = models.IntegerField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}: {self.title}"


class Activity(models.Model):
    """Registro de actividad reciente"""
    
    ACTION_TYPES = [
        ('create_card', 'Creó tarea'),
        ('delete_card', 'Eliminó tarea'),
        ('move_card', 'Movió tarea'),
        ('edit_card', 'Editó tarea'),
        ('add_comment', 'Comentó'),
        ('create_list', 'Creó lista'),
        ('delete_list', 'Eliminó lista'),
        ('add_member', 'Agregó miembro'),
        ('remove_member', 'Eliminó miembro'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities_user')
    board_id = models.IntegerField()
    card_id = models.IntegerField(null=True, blank=True)
    action = models.CharField(max_length=20, choices=ACTION_TYPES)
    description = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Activities"
    
    def __str__(self):
        return f"{self.user.username} - {self.action}"