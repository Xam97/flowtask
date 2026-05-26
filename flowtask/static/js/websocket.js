<<<<<<< HEAD
// static/js/websocket.js
// Módulo para manejo de WebSockets en FlowTask
// PREPARACIÓN: Estructura base, no implementa lógica completa todavía

=======
>>>>>>> origin/camilarodas
const FlowTaskWebSocket = (function() {
    'use strict';
    
    let socket = null;
<<<<<<< HEAD
=======
    let notificationSocket = null;
>>>>>>> origin/camilarodas
    let currentBoardId = null;
    let reconnectAttempts = 0;
    const MAX_RECONNECT_ATTEMPTS = 5;
    const RECONNECT_DELAY = 3000;
    
<<<<<<< HEAD
=======
    // Callbacks para eventos
    let eventHandlers = {
        onCardMoved: null,
        onNewComment: null,
        onCardUpdated: null,
        onCardCreated: null,
        onCardDeleted: null,
        onNotification: null
    };
    
>>>>>>> origin/camilarodas
    /**
     * Conecta al WebSocket de un tablero específico
     */
    function connectToBoard(boardId) {
<<<<<<< HEAD
        if (socket && socket.readyState === WebSocket.OPEN) {
            console.log('WebSocket ya conectado');
            return;
        }
        
        if (currentBoardId === boardId && socket) {
            return;
        }
        
        currentBoardId = boardId;
        const wsUrl = `ws://${window.location.host}/ws/board/${boardId}/`;
        
        try {
            socket = new WebSocket(wsUrl);
            
            socket.onopen = onOpen;
            socket.onclose = onClose;
            socket.onerror = onError;
            socket.onmessage = onMessage;
            
        } catch (error) {
            console.error('Error al conectar WebSocket:', error);
        }
    }
    
    /**
     * WebSocket connection opened
     */
    function onOpen(event) {
        console.log(`WebSocket conectado al tablero ${currentBoardId}`);
        reconnectAttempts = 0;
        FlowTaskHelpers.showToast('Conectado en tiempo real', 'success');
        
        // Suscribirse a notificaciones
        connectToNotifications();
    }
    
    /**
     * WebSocket connection closed
     */
    function onClose(event) {
        console.log('WebSocket desconectado');
        
        // Intentar reconectar si no es un cierre intencional
        if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS && currentBoardId) {
            reconnectAttempts++;
            const delay = RECONNECT_DELAY * reconnectAttempts;
            console.log(`Reconectando en ${delay}ms... (intento ${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})`);
            
            setTimeout(() => {
                connectToBoard(currentBoardId);
            }, delay);
        } else if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
=======
        if (!boardId) {
            console.error('Board ID es requerido');
            return;
        }
        
        // Si ya está conectado al mismo tablero, no hacer nada
        if (socket && socket.readyState === WebSocket.OPEN && currentBoardId === boardId) {
            console.log('Ya conectado al tablero', boardId);
            return;
        }
        
        // Desconectar conexión anterior si existe
        if (socket) {
            socket.close();
        }
        
        currentBoardId = boardId;
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/board/${boardId}/`;
        
        try {
            socket = new WebSocket(wsUrl);
            socket.onopen = () => onOpen('board');
            socket.onclose = (event) => onClose('board', event);
            socket.onerror = (error) => onError('board', error);
            socket.onmessage = onMessage;
        } catch (error) {
            console.error('Error al conectar WebSocket del tablero:', error);
>>>>>>> origin/camilarodas
            FlowTaskHelpers.showToast('Error de conexión en tiempo real', 'error');
        }
    }
    
    /**
<<<<<<< HEAD
     * WebSocket error
     */
    function onError(error) {
        console.error('WebSocket error:', error);
    }
    
    /**
     * Recibe mensaje del WebSocket
=======
     * Conecta al WebSocket de notificaciones
     */
    function connectToNotifications() {
        if (notificationSocket && notificationSocket.readyState === WebSocket.OPEN) {
            return;
        }
        
        if (notificationSocket) {
            notificationSocket.close();
        }
        
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/notifications/`;
        
        try {
            notificationSocket = new WebSocket(wsUrl);
            notificationSocket.onopen = () => onOpen('notifications');
            notificationSocket.onclose = (event) => onClose('notifications', event);
            notificationSocket.onerror = (error) => onError('notifications', error);
            notificationSocket.onmessage = onNotificationMessage;
        } catch (error) {
            console.error('Error al conectar WebSocket de notificaciones:', error);
        }
    }
    
    /**
     * Maneja la apertura de conexión
     */
    function onOpen(type) {
        console.log(`WebSocket ${type} conectado`);
        if (type === 'board') {
            reconnectAttempts = 0;
            FlowTaskHelpers.showToast('Conectado en tiempo real', 'success');
        }
    }
    
    /**
     * Maneja el cierre de conexión
     */
    function onClose(type, event) {
        console.log(`WebSocket ${type} desconectado`, event.code, event.reason);
        
        if (type === 'board' && currentBoardId) {
            if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
                reconnectAttempts++;
                const delay = RECONNECT_DELAY * reconnectAttempts;
                console.log(`Reconectando tablero en ${delay}ms... (intento ${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})`);
                
                setTimeout(() => {
                    connectToBoard(currentBoardId);
                }, delay);
            } else {
                FlowTaskHelpers.showToast('Sin conexión en tiempo real. Recarga la página.', 'warning');
            }
        }
        
        if (type === 'notifications' && reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
            setTimeout(() => {
                connectToNotifications();
            }, RECONNECT_DELAY);
        }
    }
    
    /**
     * Maneja errores de conexión
     */
    function onError(type, error) {
        console.error(`WebSocket ${type} error:`, error);
    }
    
    /**
     * Maneja mensajes del tablero
>>>>>>> origin/camilarodas
     */
    function onMessage(event) {
        try {
            const data = JSON.parse(event.data);
<<<<<<< HEAD
            console.log('Mensaje WebSocket recibido:', data);
            
            // TODO: Implementar handlers específicos en fase 2
            switch (data.type) {
                case 'card_moved':
                    // handleCardMoved(data);
                    break;
                case 'new_comment':
                    // handleNewComment(data);
                    break;
                case 'activity_update':
                    // handleActivityUpdate(data);
                    break;
=======
            console.log('Mensaje WebSocket recibido:', data.type);
            
            switch (data.type) {
                case 'connection_established':
                    console.log(data.message);
                    break;
                    
                case 'card_moved':
                    if (eventHandlers.onCardMoved) {
                        eventHandlers.onCardMoved(data.data);
                    }
                    // Actualizar UI automáticamente
                    updateCardPositionInUI(data.data);
                    break;
                    
                case 'new_comment':
                    if (eventHandlers.onNewComment) {
                        eventHandlers.onNewComment(data.data);
                    }
                    addCommentToUI(data.data);
                    break;
                    
                case 'card_updated':
                    if (eventHandlers.onCardUpdated) {
                        eventHandlers.onCardUpdated(data.data);
                    }
                    updateCardInUI(data.data);
                    break;
                    
                case 'card_created':
                    if (eventHandlers.onCardCreated) {
                        eventHandlers.onCardCreated(data.data);
                    }
                    addCardToUI(data.data);
                    break;
                    
                case 'card_deleted':
                    if (eventHandlers.onCardDeleted) {
                        eventHandlers.onCardDeleted(data.data);
                    }
                    removeCardFromUI(data.data.card_id);
                    break;
                    
                case 'error':
                    FlowTaskHelpers.showToast(data.message, 'error');
                    break;
                    
>>>>>>> origin/camilarodas
                default:
                    console.log('Tipo de mensaje no manejado:', data.type);
            }
        } catch (error) {
            console.error('Error al parsear mensaje WebSocket:', error);
        }
    }
    
    /**
<<<<<<< HEAD
     * Envía un mensaje a través del WebSocket
     */
    function sendMessage(message) {
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify(message));
        } else {
            console.warn('WebSocket no está conectado');
            FlowTaskHelpers.showToast('Sin conexión en tiempo real', 'warning');
=======
     * Maneja mensajes de notificaciones
     */
    function onNotificationMessage(event) {
        try {
            const data = JSON.parse(event.data);
            console.log('Notificación recibida:', data);
            
            if (data.type === 'notification') {
                // Mostrar toast
                FlowTaskHelpers.showToast(data.data.message, 'info');
                
                // Actualizar badge
                updateNotificationBadge();
                
                // Llamar callback si existe
                if (eventHandlers.onNotification) {
                    eventHandlers.onNotification(data.data);
                }
            }
        } catch (error) {
            console.error('Error al parsear notificación:', error);
>>>>>>> origin/camilarodas
        }
    }
    
    /**
<<<<<<< HEAD
     * Desconecta el WebSocket
=======
     * Envía un mensaje a través del WebSocket del tablero
     */
    function sendMessage(message) {
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify(message));
            return true;
        } else {
            console.warn('WebSocket no está conectado');
            FlowTaskHelpers.showToast('Sin conexión en tiempo real', 'warning');
            return false;
        }
    }
    
    /**
     * Mueve una tarjeta a otra lista
     */
    function moveCard(cardId, listId, position) {
        return sendMessage({
            type: 'card_move',
            card_id: cardId,
            list_id: listId,
            position: position
        });
    }
    
    /**
     * Publica un nuevo comentario
     */
    function postComment(cardId, comment) {
        return sendMessage({
            type: 'new_comment',
            card_id: cardId,
            comment: comment
        });
    }
    
    /**
     * Actualiza una tarjeta
     */
    function updateCard(cardId, field, value) {
        return sendMessage({
            type: 'card_update',
            card_id: cardId,
            field: field,
            value: value
        });
    }
    
    /**
     * Crea una nueva tarjeta
     */
    function createCard(listId, title, description) {
        return sendMessage({
            type: 'card_create',
            list_id: listId,
            title: title,
            description: description
        });
    }
    
    /**
     * Elimina una tarjeta
     */
    function deleteCard(cardId) {
        return sendMessage({
            type: 'card_delete',
            card_id: cardId
        });
    }
    
    /**
     * Desconecta todos los WebSockets
>>>>>>> origin/camilarodas
     */
    function disconnect() {
        if (socket) {
            socket.close();
            socket = null;
        }
<<<<<<< HEAD
=======
        if (notificationSocket) {
            notificationSocket.close();
            notificationSocket = null;
        }
>>>>>>> origin/camilarodas
        currentBoardId = null;
        reconnectAttempts = 0;
    }
    
    /**
<<<<<<< HEAD
     * Conecta al canal de notificaciones personales
     */
    function connectToNotifications() {
        const wsUrl = `ws://${window.location.host}/ws/notifications/`;
        const notificationSocket = new WebSocket(wsUrl);
        
        notificationSocket.onopen = () => {
            console.log('Conectado a notificaciones');
        };
        
        notificationSocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            FlowTaskHelpers.showToast(data.message, 'info');
            
            // Actualizar badge de notificaciones
            updateNotificationBadge();
        };
        
        notificationSocket.onerror = (error) => {
            console.error('Error en notificaciones:', error);
        };
    }
    
    /**
     * Actualiza el contador de notificaciones
     */
    function updateNotificationBadge() {
        // TODO: Implementar en fase 2
=======
     * Registra handlers para eventos
     */
    function on(event, callback) {
        if (eventHandlers.hasOwnProperty(event)) {
            eventHandlers[event] = callback;
        }
    }
    
    /**
     * Actualiza la posición de una tarjeta en la UI
     */
    function updateCardPositionInUI(data) {
        const cardElement = document.querySelector(`.card-item[data-card-id="${data.card_id}"]`);
        if (cardElement) {
            const targetList = document.querySelector(`.cards-container[data-list-id="${data.list_id}"]`);
            if (targetList) {
                targetList.appendChild(cardElement);
            }
        }
    }
    
    /**
     * Agrega un comentario a la UI
     */
    function addCommentToUI(data) {
        const commentsContainer = document.querySelector(`.comments-container[data-card-id="${data.card_id}"]`);
        if (commentsContainer) {
            const commentHtml = `
                <div class="comment-item" data-comment-id="${data.comment_id}">
                    <strong>${escapeHtml(data.user)}</strong>
                    <small>${data.created_at}</small>
                    <p>${escapeHtml(data.comment)}</p>
                </div>
            `;
            commentsContainer.insertAdjacentHTML('beforeend', commentHtml);
        }
    }
    
    /**
     * Actualiza una tarjeta en la UI
     */
    function updateCardInUI(data) {
        const cardElement = document.querySelector(`.card-item[data-card-id="${data.card_id}"]`);
        if (cardElement) {
            if (data.field === 'title') {
                cardElement.querySelector('.card-title').textContent = data.value;
            } else if (data.field === 'description') {
                const descElement = cardElement.querySelector('.card-description');
                if (descElement) descElement.textContent = data.value;
            }
        }
    }
    
    /**
     * Agrega una nueva tarjeta a la UI
     */
    function addCardToUI(data) {
        const targetList = document.querySelector(`.cards-container[data-list-id="${data.list_id}"]`);
        if (targetList) {
            const cardHtml = `
                <div class="card-item" data-card-id="${data.card_id}" data-position="${data.position}">
                    <div class="card-title">${escapeHtml(data.title)}</div>
                    ${data.description ? `<small class="text-muted d-block mb-2">${escapeHtml(data.description)}</small>` : ''}
                    <div class="card-footer">
                        <small>Creada por ${escapeHtml(data.created_by)}</small>
                        <button class="btn btn-sm btn-link text-danger" onclick="deleteCard(${data.card_id})">
                            <i class="fas fa-trash-alt fa-xs"></i>
                        </button>
                    </div>
                </div>
            `;
            targetList.insertAdjacentHTML('beforeend', cardHtml);
        }
    }
    
    /**
     * Elimina una tarjeta de la UI
     */
    function removeCardFromUI(cardId) {
        const cardElement = document.querySelector(`.card-item[data-card-id="${cardId}"]`);
        if (cardElement) {
            cardElement.remove();
        }
    }
    
    /**
     * Actualiza el badge de notificaciones
     */
    function updateNotificationBadge() {
>>>>>>> origin/camilarodas
        const badge = document.querySelector('.notification-icon .badge');
        if (badge) {
            const current = parseInt(badge.textContent) || 0;
            badge.textContent = current + 1;
            badge.style.display = 'inline-block';
        }
    }
    
<<<<<<< HEAD
    // API pública
    return {
        connectToBoard,
        disconnect,
        sendMessage,
=======
    /**
     * Escapa HTML para prevenir XSS
     */
    function escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    // API pública
    return {
        connectToBoard,
        connectToNotifications,
        disconnect,
        sendMessage,
        moveCard,
        postComment,
        updateCard,
        createCard,
        deleteCard,
        on
>>>>>>> origin/camilarodas
    };
})();

// Exponer globalmente
window.FlowTaskWebSocket = FlowTaskWebSocket;