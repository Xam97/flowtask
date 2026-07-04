from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ContactRequest

User = get_user_model()

class UserSearchSerializer(serializers.ModelSerializer):
    contact_status = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'contact_status']

    def get_contact_status(self, obj):
        request_user = self.context.get('request').user
        if not request_user or request_user.is_anonymous:
            return 'none'

        # Buscamos si existe una relación previa entre el usuario logueado y el resultado de la búsqueda
        relation = ContactRequest.objects.get_relation_status(request_user, obj)

        if not relation:
            return 'none'
        
        if relation.status == 'accepted':
            return 'accepted'
        
        if relation.status == 'pending':
            # Diferenciamos si fui yo quien la envió o si fui yo quien la recibió
            return 'pending_sent' if relation.sender == request_user else 'pending_received'
            
        return 'none'