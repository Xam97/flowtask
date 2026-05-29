# Vistas de autenticación: registro, login, logout
# Implementa validaciones backend y protección CSRF

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

# ========== REGISTRO ==========
@csrf_protect
@require_http_methods(["GET", "POST"])
def register_view(request):
    """
    Vista de registro de nuevos usuarios.
    Valida backend:
    - Nombre de usuario único
    - Contraseña segura (mínimo 8 caracteres)
    - Confirmación de contraseña
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '¡Registro exitoso! Bienvenido a FlowTask.')
            return redirect('dashboard')
        else:
            # Mostrar errores específicos
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = UserCreationForm()
    
    return render(request, 'auth/register.html', {'form': form})

# ========== LOGIN ==========
@csrf_protect
@require_http_methods(["GET", "POST"])
def login_view(request):
    """
    Vista de inicio de sesión.
    Autentica usuario y contraseña.
    Protegida contra CSRF.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'¡Bienvenido de vuelta, {username}!')
                
                # Redirigir a la página solicitada originalmente o dashboard
                next_url = request.GET.get('next', 'dashboard')
                return redirect(next_url)
        # IMPORTANTE: NO usar messages.error aquí
        # En su lugar, pasamos el error al formulario
        else:
            # Agregar error al formulario para mostrarlo debajo del campo
            form.add_error('password', 'Usuario o contraseña incorrectos. Por favor, intenta nuevamente.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'auth/login.html', {'form': form})

# ========== LOGOUT ==========
@login_required
@require_http_methods(["POST"])
def logout_view(request):
    """
    Cierre de sesión.
    Solo permite método POST para evitar CSRF.
    """
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente.')
    return redirect('login')

# ========== DASHBOARD (PROTEGIDO) ==========
@login_required
def dashboard_view(request):
    """
    Dashboard principal del usuario.
    Solo accesible para usuarios autenticados.
    """
    # Obtener tableros del usuario (propios + donde es miembro)
    from boards.models import Board
    
    owned_boards = request.user.owned_boards.filter(is_archived=False)
    member_boards = request.user.boards.filter(is_archived=False)
    
    context = {
        'owned_boards': owned_boards,
        'member_boards': member_boards,
    }
    return render(request, 'dashboard.html', context)