const FlowTaskHelpers = (function() {
    'use strict';
    
    /**
     * Obtiene el token CSRF de la cookie
     */
    function getCSRFToken() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='));
        
        return cookieValue ? cookieValue.split('=')[1] : '';
    }
    
    /**
     * Wrapper para fetch con configuración automática
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
     * Muestra un toast notification
     */
    function showToast(message, type = 'info') {
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            container.style.zIndex = '9999';
            document.body.appendChild(container);
        }
        
        const toastId = 'toast-' + Date.now();
        const bgColor = type === 'error' ? 'bg-danger' : type === 'success' ? 'bg-success' : 'bg-primary';
        
        const toastHtml = `
            <div id="${toastId}" class="toast" role="alert" data-bs-autohide="true" data-bs-delay="3000">
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
        
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    }
    
    /**
     * Formatea fecha para mostrar
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
     * Debounce para optimizar eventos frecuentes
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
     * Escapa HTML para prevenir XSS
     */
    function escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    return {
        getCSRFToken,
        apiFetch,
        showToast,
        formatDate,
        debounce,
        escapeHtml
    };
})();

window.FlowTaskHelpers = FlowTaskHelpers;

    /**
     * Muestra un loader/spinner
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
     * Oculta el loader
     */
    function hideLoader(containerId) {
        const container = document.getElementById(containerId);
        if (container) {
            const loader = container.querySelector('.loader-spinner');
            if (loader) loader.remove();
        }
    }
    
    /**
     * Confirmación con modal personalizada
     */
    function confirmAction(message, onConfirm, onCancel) {
        const confirmed = confirm(message);
        if (confirmed && onConfirm) onConfirm();
        if (!confirmed && onCancel) onCancel();
        return confirmed;
    }