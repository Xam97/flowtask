# Estructura: Board (tablero) -> List (lista) -> Card (tarjeta)

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator, MaxLengthValidator
from decimal import Decimal

# ========== BOARD (TABLERO) ==========
class Board(models.Model):
    """
    Tablero principal que contiene listas y tarjetas.
    Cada tablero pertenece a un propietario y puede tener múltiples miembros.
    """
    # Información básica
    name = models.CharField(
        max_length=100,
        validators=[MinLengthValidator(3)],
        help_text="Nombre del tablero (mínimo 3 caracteres)"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Descripción opcional del tablero"
    )
    
    # Relaciones
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_boards',
        help_text="Usuario propietario del tablero"
    )
    members = models.ManyToManyField(
        User, 
        related_name='boards', 
        blank=True,
        help_text="Miembros colaboradores del tablero"
    )
    
    # Configuración
    is_archived = models.BooleanField(
        default=False,
        help_text="Indica si el tablero está archivado"
    )
    
    # Timestamps (usarán zona horaria America/Asuncion automáticamente)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Tablero"
        verbose_name_plural = "Tableros"

    def save(self, *args, **kwargs):
        """Guardar el board y agregar al owner como miembro automáticamente"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Si es un board nuevo, agregar al owner como miembro
        # if is_new and self.owner:
        #     if not self.members.filter(id=self.owner.id).exists():
        #         self.members.add(self.owner)    
    
    def __str__(self):
        return self.name
    
    def get_card_count(self):
        """Retorna el número total de tarjetas en el tablero"""
        return Card.objects.filter(list__board=self).count()
        

# ========== MEMBERSHIP (RELACIÓN USUARIO-TABLERO) ==========
class Membership(models.Model):
    """
    Modelo intermedio para gestionar la membresía de usuarios en tableros.
    Permite definir roles y permisos específicos.
    """
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
        unique_together = ['user', 'board']  # Evita membresías duplicadas
        verbose_name = "Membresía"
        verbose_name_plural = "Membresías"
    
    def __str__(self):
        return f"{self.user.username} - {self.board.name} ({self.role})"

# ========== LIST (LISTA DENTRO DEL TABLERO) ==========
class List(models.Model):
    """
    Lista Kanban dentro de un tablero (Ej: Pendiente, En proceso, Terminado).
    Utiliza DecimalField para ordenamiento preciso entre listas.
    """
    name = models.CharField(
        max_length=100,
        validators=[MinLengthValidator(1)],
        help_text="Nombre de la lista (ej: Pendiente, En proceso)"
    )
    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name='lists',
        help_text="Tablero al que pertenece esta lista"
    )
    
    # Posición para ordenamiento (usando Decimal para insertar entre posiciones)
    # Ejemplo: 10.0, 20.0, 30.0 permite insertar en medio con 15.0
    position = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Posición para ordenar las listas (Decimal permite inserción flexible)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['position', 'created_at']
        verbose_name = "Lista"
        verbose_name_plural = "Listas"
    
    def __str__(self):
        return f"{self.name} ({self.board.name})"
    
    def save(self, *args, **kwargs):
        """Asigna posición automática si no existe"""
        if not self.position:
            # Obtener la posición máxima actual + 10
            max_position = List.objects.filter(board=self.board).aggregate(
                models.Max('position')
            )['position__max']
            self.position = (max_position or 0) + 10
        super().save(*args, **kwargs)

# ========== CARD (TARJETA/TAREA) ==========
class Card(models.Model):
    """
    Tarjeta o tarea individual dentro de una lista Kanban.
    Contiene toda la información de la tarea.
    """
    PRIORITY_CHOICES = [
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
        ('urgent', 'Urgente'),
    ]
    
    # Información básica
    title = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(3)],
        help_text="Título de la tarea"
    )
    description = models.TextField(
        blank=True,
        help_text="Descripción detallada de la tarea"
    )
    
    # Relaciones
    list = models.ForeignKey(
        List,
        on_delete=models.CASCADE,
        related_name='cards',
        help_text="Lista Kanban donde se encuentra la tarjeta"
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_cards',
        help_text="Usuario asignado a esta tarea"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_cards',
        help_text="Usuario que creó la tarjeta"
    )
    
    # Configuración
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        help_text="Prioridad de la tarea"
    )
    due_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha límite para completar la tarea"
    )
    
    # Posición para ordenamiento entre tarjetas de la misma lista
    position = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Posición para ordenar tarjetas dentro de la lista"
    )
    
    is_completed = models.BooleanField(
        default=False,
        help_text="Indica si la tarea está completada"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['position', '-created_at']
        verbose_name = "Tarjeta"
        verbose_name_plural = "Tarjetas"
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        """Asigna posición automática si no existe"""
        if not self.position:
            max_position = Card.objects.filter(list=self.list).aggregate(
                models.Max('position')
            )['position__max']
            self.position = (max_position or 0) + 10
        super().save(*args, **kwargs)

# ============================================
# MODELOS PARA FASE 3 (TIEMPO REAL)
# ============================================

class Comment(models.Model):
    """Comentarios en tareas"""
    task = models.ForeignKey('Card', on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comentario de {self.author.email} en {self.task.title[:20]}"


class Notification(models.Model):
    """Notificaciones para usuarios"""
    NOTIFICATION_TYPES = (
        ('task_assigned', 'Tarea asignada'),
        ('comment_added', 'Nuevo comentario'),
        ('task_moved', 'Tarea movida'),
        ('mention', 'Mencionado'),
    )
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications', null=True, blank=True)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    task = models.ForeignKey('Card', on_delete=models.CASCADE, null=True, blank=True)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notificación para {self.recipient.email}: {self.message[:30]}"


class Activity(models.Model):
    """Registro de actividad en tableros"""
    ACTION_TYPES = (
        ('task_created', 'Tarea creada'),
        ('task_updated', 'Tarea actualizada'),
        ('task_moved', 'Tarea movida'),
        ('task_deleted', 'Tarea eliminada'),
        ('comment_added', 'Comentario agregado'),
        ('member_added', 'Miembro agregado'),
        ('member_removed', 'Miembro removido'),
    )
    
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='activities')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    task = models.ForeignKey('Card', on_delete=models.CASCADE, null=True, blank=True)
    old_list = models.ForeignKey(List, on_delete=models.SET_NULL, null=True, blank=True, related_name='old_activities')
    new_list = models.ForeignKey(List, on_delete=models.SET_NULL, null=True, blank=True, related_name='new_activities')
    details = models.JSONField(default=dict, blank=True)  # Para almacenar detalles adicionales
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Activities"
    
    def __str__(self):
        return f"{self.user.email} - {self.get_action_type_display()} en {self.board.name}"