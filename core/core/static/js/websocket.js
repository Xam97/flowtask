// static/js/websocket.js
// Módulo para manejo de WebSockets en FlowTask
// PREPARACIÓN: Estructura base, no implementa lógica completa todavía

const FlowTaskWebSocket = (function() {
    'use strict';
    
    let socket = null;
    let currentBoardId = null;
    let reconnectAttempts = 0;
    const MAX_RECONNECT_ATTEMPTS = 5;
    const RECONNECT_DELAY = 3000;
    
    /**
     * Conecta al WebSocket de un tablero específico
     */
    function connectToBoard(boardId) {
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
            FlowTaskHelpers.showToast('Error de conexión en tiempo real', 'error');
        }
    }
    
    /**
     * WebSocket error
     */
    function onError(error) {
        console.error('WebSocket error:', error);
    }
    
    /**
     * Recibe mensaje del WebSocket
     */
    function onMessage(event) {
        try {
            const data = JSON.parse(event.data);
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
                default:
                    console.log('Tipo de mensaje no manejado:', data.type);
            }
        } catch (error) {
            console.error('Error al parsear mensaje WebSocket:', error);
        }
    }
    
    /**
     * Envía un mensaje a través del WebSocket
     */
    function sendMessage(message) {
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify(message));
        } else {
            console.warn('WebSocket no está conectado');
            FlowTaskHelpers.showToast('Sin conexión en tiempo real', 'warning');
        }
    }
    
    /**
     * Desconecta el WebSocket
     */
    function disconnect() {
        if (socket) {
            socket.close();
            socket = null;
        }
        currentBoardId = null;
        reconnectAttempts = 0;
    }
    
    /**
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
        const badge = document.querySelector('.notification-icon .badge');
        if (badge) {
            const current = parseInt(badge.textContent) || 0;
            badge.textContent = current + 1;
            badge.style.display = 'inline-block';
        }
    }
    
    // API pública
    return {
        connectToBoard,
        disconnect,
        sendMessage,
    };
})();

// Exponer globalmente
window.FlowTaskWebSocket = FlowTaskWebSocket;