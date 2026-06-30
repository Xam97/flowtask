from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class ContactRequestQuerySet(models.QuerySet):
    def get_relation_status(self, user1, user2):
        """Devuelve la fila de la relación activa entre dos usuarios si existe."""
        return self.filter(
            (Q(sender=user1) & Q(receiver=user2)) | 
            (Q(sender=user2) & Q(receiver=user1))
        ).first()

class ContactRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('accepted', 'Aceptada'),
        ('rejected', 'Rechazada'),
    ]

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_contact_requests')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_contact_requests')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ContactRequestQuerySet.as_manager()

    class Meta:
        unique_together = ('sender', 'receiver')
        verbose_name = 'Solicitud de contacto'
        verbose_name_plural = 'Solicitudes de contacto'

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username} ({self.status})"