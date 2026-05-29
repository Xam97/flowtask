# boards/validators.py
from django.core.exceptions import ValidationError
import re

class CustomPasswordValidator:
    """Validador de contraseña con requisitos adicionales"""
    
    def validate(self, password, user=None):
        errors = []
        
        # Requiere al menos una mayúscula
        if not re.search(r'[A-Z]', password):
            errors.append('La contraseña debe contener al menos una letra mayúscula.')
        
        # Requiere al menos una minúscula
        if not re.search(r'[a-z]', password):
            errors.append('La contraseña debe contener al menos una letra minúscula.')
        
        # Requiere al menos un número
        if not re.search(r'[0-9]', password):
            errors.append('La contraseña debe contener al menos un número.')
        
        # Requiere al menos un caracter especial
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append('La contraseña debe contener al menos un caracter especial (!@#$%^&*(),.?":{}|<>).')
        
        if errors:
            raise ValidationError(' '.join(errors))
    
    def get_help_text(self):
        return """
        Tu contraseña debe contener:
        - Al menos 8 caracteres
        - Al menos una letra mayúscula
        - Al menos una letra minúscula
        - Al menos un número
        - Al menos un caracter especial
        """