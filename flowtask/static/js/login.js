// static/js/login.js
// Validaciones del formulario de login

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('loginForm');
    if (!form) return;
    
    const username = document.getElementById('id_username');
    const password = document.getElementById('id_password');
    
    // Función para limpiar error al escribir
    function clearErrorOnInput(input, groupId) {
        input.addEventListener('input', function() {
            const group = document.getElementById(groupId);
            const errorDiv = group.querySelector('.error-message');
            if (errorDiv) {
                errorDiv.style.display = 'none';
                input.classList.remove('error');
            }
            
            // También limpiar errores no relacionados al campo (non_field_errors)
            const nonFieldError = document.querySelector('.non-field-error');
            if (nonFieldError) {
                nonFieldError.style.display = 'none';
            }
        });
    }
    
    // Validar antes de enviar
    if (form) {
        form.addEventListener('submit', function(e) {
            let hasError = false;
            
            // Limpiar errores previos
            document.querySelectorAll('.error-message').forEach(div => {
                div.style.display = 'none';
            });
            document.querySelectorAll('.form-control').forEach(input => {
                input.classList.remove('error');
            });
            
            // Validar usuario
            if (!username.value.trim()) {
                const group = document.getElementById('username-group');
                let errorDiv = group.querySelector('.error-message');
                if (!errorDiv) {
                    errorDiv = document.createElement('div');
                    errorDiv.className = 'error-message';
                    group.appendChild(errorDiv);
                }
                errorDiv.innerHTML = '<i class="fas fa-exclamation-circle"></i> El usuario es obligatorio';
                errorDiv.style.display = 'flex';
                username.classList.add('error');
                hasError = true;
            }
            
            // Validar contraseña
            if (!password.value) {
                const group = document.getElementById('password-group');
                let errorDiv = group.querySelector('.error-message');
                if (!errorDiv) {
                    errorDiv = document.createElement('div');
                    errorDiv.className = 'error-message';
                    group.appendChild(errorDiv);
                }
                errorDiv.innerHTML = '<i class="fas fa-exclamation-circle"></i> La contraseña es obligatoria';
                errorDiv.style.display = 'flex';
                password.classList.add('error');
                hasError = true;
            }
            
            if (hasError) {
                e.preventDefault();
            }
        });
    }
    
    // Limpiar errores al escribir
    if (username) {
        clearErrorOnInput(username, 'username-group');
    }
    if (password) {
        clearErrorOnInput(password, 'password-group');
    }
    
    // Si hay error del servidor (contraseña incorrecta), limpiar solo el campo contraseña
    const serverError = document.querySelector('#password-group .error-message');
    if (serverError && serverError.style.display !== 'none') {
        if (password) {
            password.value = '';
            password.focus();
        }
    }
});