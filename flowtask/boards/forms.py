# Formularios para validación de datos en boards

from django import forms
from .models import Board, List, Card

class BoardForm(forms.ModelForm):
    """Formulario para crear/editar tableros con validación"""
    
    class Meta:
        model = Board
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del tablero'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción (opcional)'
            })
        }
    
    def clean_name(self):
        """Validar que el nombre no esté vacío y tenga al menos 3 caracteres"""
        name = self.cleaned_data.get('name')
        if not name or len(name.strip()) < 3:
            raise forms.ValidationError('El nombre debe tener al menos 3 caracteres')
        return name.strip()


class ListForm(forms.ModelForm):
    """Formulario para crear/editar listas"""
    
    class Meta:
        model = List
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la lista'
            })
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name or len(name.strip()) < 1:
            raise forms.ValidationError('El nombre es requerido')
        return name.strip()


class CardForm(forms.ModelForm):
    """Formulario para crear/editar tarjetas"""
    
    class Meta:
        model = Card
        fields = ['title', 'description', 'priority', 'assigned_to', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título de la tarea'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción detallada'
            }),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
        }
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title or len(title.strip()) < 3:
            raise forms.ValidationError('El título debe tener al menos 3 caracteres')
        return title.strip()