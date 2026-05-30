# boards/models.py
# Solo modelos principales - SIN duplicados

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator, MaxLengthValidator
from decimal import Decimal


class Board(models.Model):
    """Tablero principal que contiene listas y tarjetas"""
    name = models.CharField(max_length=100, validators=[MinLengthValidator(3)])
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_boards')
    members = models.ManyToManyField(User, through='Membership', related_name='boards')
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_card_count(self):
        return Card.objects.filter(list__board=self).count()


class Membership(models.Model):
    """Modelo intermedio para membresía de usuarios en tableros"""
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('member', 'Miembro'),
        ('viewer', 'Espectador'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'board']
    
    def __str__(self):
        return f"{self.user.username} - {self.board.name} ({self.role})"


class List(models.Model):
    """Lista Kanban dentro de un tablero"""
    name = models.CharField(max_length=100, validators=[MinLengthValidator(1)])
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='lists')
    position = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['position', 'created_at']
    
    def __str__(self):
        return f"{self.name} ({self.board.name})"
    
    def save(self, *args, **kwargs):
        if not self.position:
            max_position = List.objects.filter(board=self.board).aggregate(
                models.Max('position')
            )['position__max'] or 0
            self.position = (max_position or 0) + 10
        super().save(*args, **kwargs)


class Card(models.Model):
    """Tarjeta o tarea individual dentro de una lista"""
    PRIORITY_CHOICES = [
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
        ('urgent', 'Urgente'),
    ]
    
    title = models.CharField(max_length=200, validators=[MinLengthValidator(3)])
    description = models.TextField(blank=True)
    list = models.ForeignKey(List, on_delete=models.CASCADE, related_name='cards')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_cards')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_cards')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    due_date = models.DateTimeField(null=True, blank=True)
    position = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['position', '-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.position:
            max_position = Card.objects.filter(list=self.list).aggregate(
                models.Max('position')
            )['position__max'] or 0
            self.position = (max_position or 0) + 10
        super().save(*args, **kwargs)