# boards/serializers.py
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import Board, List, Card

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer para registro con validaciones robustas"""
    
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message='Este email ya está registrado.')]
    )
    username = serializers.CharField(
        required=True,
        validators=[
            UniqueValidator(queryset=User.objects.all(), message='Este nombre de usuario ya existe.'),
        ]
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        label='Confirmar contraseña'
    )
    first_name = serializers.CharField(required=True, max_length=30)
    last_name = serializers.CharField(required=True, max_length=30)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password', 'password2')
    
    def validate_username(self, value):
        """Validar que el username no tenga caracteres especiales"""
        import re
        if not re.match(r'^[\w.@+-]+$', value):
            raise serializers.ValidationError(
                'El nombre de usuario solo puede contener letras, números y los caracteres .@+-'
            )
        if len(value) < 3:
            raise serializers.ValidationError(
                'El nombre de usuario debe tener al menos 3 caracteres.'
            )
        return value
    
    def validate(self, attrs):
        """Validar que las contraseñas coincidan"""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {'password': 'Las contraseñas no coinciden.'}
            )
        return attrs
    
    def create(self, validated_data):
        """Crear usuario con contraseña hasheada"""
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializer básico de usuario (solo lectura)"""
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')
        read_only_fields = ('id',)

