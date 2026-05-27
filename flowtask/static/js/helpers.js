// static/js/helpers.js
// Utilidades JavaScript reutilizables para FlowTask
// Módulo con funciones helper para CSRF, fetch, etc.

const FlowTaskHelpers = (function() {
    'use strict';
    
    /**
     * Obtiene el token CSRF de la cookie
     * Necesario para todas las peticiones fetch POST/PUT/DELETE
     */
    function getCSRFToken() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='));
        
        return cookieValue ? cookieValue.split('=')[1] : '';
    }
    
    /**
     * Wrapper para fetch con configuración automática
     * Incluye headers, CSRF, y manejo de errores
     */
    async function apiFetch(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            credentials: 'same-origin',
        };
        
        const mergedOptions = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...options.headers,
            },
        };
        
        try {
            const response = await fetch(url, mergedOptions);
            
            if (!response.ok) {
                const error = await response.json().catch(() => ({}));
                throw new Error(error.message || `HTTP ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            showToast('Error: ' + error.message, 'error');
            throw error;
        }
    }
    
    /**
     * Muestra un toast notification con colores dinámicos (Bootstrap 5)
     */
    function showToast(message, type = 'info') {
        // Crear contenedor de toasts si no existe
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            container.style.zIndex = '9999';
            document.body.appendChild(container);
        }
        
        // Asignar color según el tipo de alerta
        const toastId = 'toast-' + Date.now();
        const bgColor = type === 'error' ? 'bg-danger' : type === 'success' ? 'bg-success' : 'bg-primary';
        
        const toastHtml = `
            <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true" data-bs-autohide="true" data-bs-delay="3000">
                <div class="toast-header ${bgColor} text-white">
                    <i class="fas fa-bell me-2"></i>
                    <strong class="me-auto">FlowTask</strong>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
                </div>
                <div class="toast-body">
                    ${message}
                </div>
            </div>
        `;
        
        container.insertAdjacentHTML('beforeend', toastHtml);
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement);
        toast.show();
        
        // Remover del DOM después de ocultar
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    }
    
    /**
     * Formatea fecha para mostrar con el estándar regional local
     */
    function formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('es-PY', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
    
    /**
     * Debounce para optimizar eventos frecuentes (ej: búsqueda)
     */
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    /**
     * Escapa HTML para prevenir vulnerabilidades XSS
     */
    function escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    /**
     * Muestra un loader/spinner dentro de un contenedor
     */
    function showLoader(containerId) {
        const container = document.getElementById(containerId);
        if (container) {
            const loader = document.createElement('div');
            loader.className = 'loader-spinner';
            loader.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Cargando...</span></div>';
            container.appendChild(loader);
        }
    }
    
    /**
     * Oculta el loader de un contenedor
     */
    function hideLoader(containerId) {
        const container = document.getElementById(containerId);
        if (container) {
            const loader = container.querySelector('.loader-spinner');
            if (loader) loader.remove();
        }
    }
    
    /**
     * Confirmación con ventana nativa simplificada
     */
    function confirmAction(message, onConfirm, onCancel) {
        const confirmed = confirm(message);
        if (confirmed && onConfirm) onConfirm();
        if (!confirmed && onCancel) onCancel();
        return confirmed;
    }
    
    // API pública de utilidades
    return {
        getCSRFToken,
        apiFetch,
        showToast,
        formatDate,
        debounce,
        escapeHtml,
        showLoader,
        hideLoader,
        confirmAction
    };
})();

// Exponer globalmente para los demás scripts de la app
window.FlowTaskHelpers = FlowTaskHelpers;