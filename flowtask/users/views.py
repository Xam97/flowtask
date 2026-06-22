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
                next_url = request.GET.get('next', 'dashboard')
                return redirect(next_url)
        else:
            form.add_error('password', 'Usuario o contraseña incorrectos. Por favor, intenta nuevamente.')
    else:
        form = AuthenticationForm()

    return render(request, 'auth/login.html', {'form': form})


# ========== LOGOUT ==========
@login_required
@require_http_methods(["POST"])
def logout_view(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente.')
    return redirect('login')


# ========== PERFIL ==========
@login_required
def profile_view(request):
    from boards.models import Card
    from boards.utils import get_user_boards

    user = request.user
    boards = get_user_boards(user)
    stats = {
        'boards': boards.count(),
        'tasks_created': Card.objects.filter(created_by=user).count(),
        'tasks_assigned': Card.objects.filter(assigned_to=user, is_completed=False).count(),
        'tasks_completed': Card.objects.filter(assigned_to=user, is_completed=True).count(),
    }

    return render(request, 'users/profile.html', {
        'profile_user': user,
        'stats': stats,
    })


# ========== PREFERENCIAS ==========
@csrf_protect
@login_required
@require_http_methods(['GET', 'POST'])
def preferences_view(request):
    if request.method == 'POST':
        messages.success(request, 'Preferencias guardadas correctamente')
        return redirect('preferences')

    return render(request, 'users/preferences.html')


# ========== DASHBOARD (PROTEGIDO) ==========
@login_required
def dashboard_view(request):
    from boards.models import Card
    from boards.utils import get_user_boards
    from django.utils import timezone

    owned_boards = request.user.owned_boards.filter(is_archived=False)
    member_boards = request.user.boards.filter(is_archived=False).exclude(owner=request.user)

    board_ids = list(get_user_boards(request.user).values_list('id', flat=True))
    now = timezone.now()
    stats = {
        'total_boards': len(board_ids),
        'pending_tasks': Card.objects.filter(list__board_id__in=board_ids, is_completed=False).count(),
        'completed_tasks': Card.objects.filter(list__board_id__in=board_ids, is_completed=True).count(),
        'due_soon': Card.objects.filter(
            list__board_id__in=board_ids,
            due_date__gte=now,
            due_date__lte=now + timezone.timedelta(days=7),
            is_completed=False,
        ).count(),
    }

    return render(request, 'dashboard.html', {
        'owned_boards': owned_boards,
        'member_boards': member_boards,
        'stats': stats,
    })
