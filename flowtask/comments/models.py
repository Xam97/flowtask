# comments/models.py

from django.db import models
from django.contrib.auth.models import User
from boards.models import Card


class Comment(models.Model):
    """Comentarios en tarjetas"""
    
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='comments_card')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments_user')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = "Comentario"
        verbose_name_plural = "Comentarios"
    
    def __str__(self):
        return f"{self.user.username}: {self.content[:50]}"