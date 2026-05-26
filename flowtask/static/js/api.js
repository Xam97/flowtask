// Módulo para peticiones AJAX con fetch

const FlowTaskAPI = (function() {
    'use strict';
    
    /**
     * Realiza una petición fetch con manejo automático de CSRF
     */
    async function request(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': FlowTaskHelpers.getCSRFToken(),
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
            FlowTaskHelpers.showToast(error.message, 'error');
            throw error;
        }
    }
    
    /**
     * Actualizar posición de una tarjeta
     */
    async function updateCardPosition(cardId, listId, position) {
        return request('/boards/cards/update-position/', {
            method: 'POST',
            body: JSON.stringify({
                card_id: cardId,
                list_id: listId,
                position: position * 10
            })
        });
    }
    
    /**
     * Actualizar posición de una lista
     */
    async function updateListPosition(listId, position) {
        return request('/boards/lists/update-position/', {
            method: 'POST',
            body: JSON.stringify({
                list_id: listId,
                position: position * 10
            })
        });
    }
    
    /**
     * Eliminar una tarjeta
     */
    async function deleteCard(cardId) {
        return request(`/boards/cards/${cardId}/delete/`, {
            method: 'POST'
        });
    }
    
    /**
     * Eliminar una lista
     */
    async function deleteList(listId) {
        return request(`/boards/lists/${listId}/delete/`, {
            method: 'POST'
        });
    }
    
    return {
        request,
        updateCardPosition,
        updateListPosition,
        deleteCard,
        deleteList
    };
})();

window.FlowTaskAPI = FlowTaskAPI;