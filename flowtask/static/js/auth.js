// static/js/auth.js
// Validaciones del formulario de registro - FlowTask

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('registerForm');
    if (!form) return; // Salir si no estamos en la página de registro
    
    const password1 = document.getElementById('id_password1');
    const password2 = document.getElementById('id_password2');
    const username = document.getElementById('id_username');
    
    // Lista de contraseñas comunes
    const commonPasswords = [
        '12345678', 'password', 'qwerty123', 'abc12345', 
        '123456789', 'admin123', '1234567890', 'password123'
    ];
    
    // Función para obtener el primer error de contraseña
    function getFirstPasswordError(password) {
        if (password.length === 0) return null;
        if (password.length < 8) {
            return 'La contraseña debe tener al menos 8 caracteres';
        }
        if (!/[A-Z]/.test(password)) {
            return 'Debe contener al menos una letra mayúscula';
        }
        if (!/[a-z]/.test(password)) {
            return 'Debe contener al menos una letra minúscula';
        }
        if (!/[0-9]/.test(password)) {
            return 'Debe contener al menos un número';
        }
        if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
            return 'Debe contener al menos un caracter especial';
        }
        if (/^\d+$/.test(password)) {
            return 'No puede ser completamente numérica';
        }
        if (commonPasswords.includes(password.toLowerCase())) {
            return 'Esta contraseña es demasiado común';
        }
        return null;
    }
    
    // Función para mostrar error
    function showError(input, message, groupId) {
        const group = document.getElementById(groupId);
        let errorDiv = group.querySelector('.error-message');
        
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'error-message';
            group.appendChild(errorDiv);
        }
        
        errorDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
        errorDiv.style.display = 'flex';
        input.classList.add('error');
    }
    
    // Función para limpiar error
    function clearError(input, groupId) {
        const group = document.getElementById(groupId);
        const errorDiv = group.querySelector('.error-message');
        if (errorDiv && errorDiv.style.display !== 'none') {
            // Solo ocultar si es un error de validación en tiempo real
            // No ocultar errores del servidor
            if (!errorDiv.hasAttribute('data-server-error')) {
                errorDiv.style.display = 'none';
            }
        }
        input.classList.remove('error');
    }
    
    // Marcar errores del servidor
    function markServerErrors() {
        document.querySelectorAll('.error-message').forEach(div => {
            if (div.style.display !== 'none') {
                div.setAttribute('data-server-error', 'true');
            }
        });
    }
    
    // Validar usuario
    if (username) {
        username.addEventListener('input', function() {
            const value = this.value;
            
            if (value.length > 150) {
                showError(this, 'El usuario no puede tener más de 150 caracteres', 'username-group');
            } else if (value.length > 0 && !/^[\w.@+-]+$/.test(value)) {
                showError(this, 'El usuario solo puede contener letras, números y @/./+/-/_', 'username-group');
            } else {
                clearError(this, 'username-group');
            }
        });
    }
    
    // Validar contraseña en tiempo real
    if (password1) {
        password1.addEventListener('input', function() {
            const password = this.value;
            const error = getFirstPasswordError(password);
            
            if (error) {
                showError(this, error, 'password1-group');
            } else {
                clearError(this, 'password1-group');
                // Si la contraseña es válida, verificar coincidencia
                if (password2 && password2.value) {
                    password2.dispatchEvent(new Event('input'));
                }
            }
        });
    }
    
    // Validar coincidencia de contraseñas
    if (password2) {
        password2.addEventListener('input', function() {
            const pwd1 = password1.value;
            const pwd2 = this.value;
            
            if (pwd2.length > 0 && pwd1 !== pwd2) {
                showError(this, 'Las contraseñas no coinciden', 'password2-group');
            } else if (pwd2.length > 0 && pwd1 === pwd2) {
                clearError(this, 'password2-group');
            } else if (pwd2.length === 0) {
                clearError(this, 'password2-group');
            }
        });
    }
    
    // Validar antes de enviar
    if (form) {
        form.addEventListener('submit', function(e) {
            let hasError = false;
            
            // Verificar usuario
            if (username && username.value.trim() === '') {
                showError(username, 'El usuario es obligatorio', 'username-group');
                hasError = true;
            } else if (username && username.value.length > 150) {
                showError(username, 'El usuario no puede tener más de 150 caracteres', 'username-group');
                hasError = true;
            }
            
            // Verificar contraseña
            if (password1) {
                const passwordError = getFirstPasswordError(password1.value);
                if (passwordError) {
                    showError(password1, passwordError, 'password1-group');
                    hasError = true;
                }
            }
            
            // Verificar coincidencia
            if (password2 && password1.value !== password2.value) {
                showError(password2, 'Las contraseñas no coinciden', 'password2-group');
                hasError = true;
            }
            
            if (hasError) {
                e.preventDefault();
                // Scroll al primer error
                const firstError = document.querySelector('.error-message[style*="display: flex"]');
                if (firstError) {
                    firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }
        });
    }
    
    // Marcar errores existentes del servidor
    markServerErrors();
});