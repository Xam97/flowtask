// static/js/notifications.js
let notificationsWebSocket = null;

document.addEventListener('DOMContentLoaded', function() {
    initNotifications();
    initNotificationsWebSocket();
});

function initNotifications() {
    // Cargar notificaciones cuando se abre el dropdown
    const dropdown = document.getElementById('notifications-dropdown');
    const bell = document.getElementById('notificationsBell');
    
    if (dropdown && bell) {
        // Usar evento de Bootstrap 5
        bell.addEventListener('click', function(e) {
            // Pequeño delay para que Bootstrap abra el dropdown
            setTimeout(() => {
                loadNotifications();
            }, 100);
        });
    }
    
    // Marcar todas como leídas
    const markAllBtn = document.getElementById('mark-all-read-btn');
    if (markAllBtn) {
        markAllBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            markAllNotificationsAsRead();
        });
    }
}

function loadNotifications() {
    fetch('/notifications/api/get/?limit=10')
        .then(response => response.json())
        .then(data => {
            updateNotificationBadge(data.unread_count);
            renderNotificationsList(data.notifications);
        })
        .catch(error => {
            console.error('Error cargando notificaciones:', error);
            const container = document.getElementById('notifications-list');
            if (container) {
                container.innerHTML = `
                    <div class="empty-notifications">
                        <i class="fas fa-exclamation-circle"></i>
                        <p>Error al cargar notificaciones</p>
                    </div>
                `;
            }
        });
}

function renderNotificationsList(notifications) {
    const container = document.getElementById('notifications-list');
    
    if (!container) return;
    
    if (!notifications || notifications.length === 0) {
        container.innerHTML = `
            <div class="empty-notifications">
                <i class="fas fa-bell-slash"></i>
                <p>No tienes notificaciones</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = notifications.map(notification => `
        <div class="notification-item ${!notification.is_read ? 'unread' : ''}" 
             data-id="${notification.id}" 
             data-read="${notification.is_read}"
             data-board-id="${notification.board_id || ''}"
             data-card-id="${notification.card_id || ''}">
            <div class="notification-icon-custom ${getIconColor(notification.type)}">
                <i class="${getIconClass(notification.type)}"></i>
            </div>
            <div class="notification-content">
                <div class="notification-message">${escapeHtml(notification.message)}</div>
                <div class="notification-time">${formatTime(notification.created_at)}</div>
            </div>
            ${!notification.is_read ? '<div class="notification-badge-unread"></div>' : ''}
        </div>
    `).join('');
    
    // Asignar eventos click
    setupNotificationClickEvents();
}

// 💡 Separamos los eventos en una función reutilizable
function setupNotificationClickEvents() {
    document.querySelectorAll('.notification-item').forEach(item => {
        // Remover el listener anterior para evitar duplicados si se vuelve a renderizar
        item.removeEventListener('click', handleNotificationClick);
        item.addEventListener('click', handleNotificationClick);
    });
}

function handleNotificationClick(e) {
    e.stopPropagation();
    const id = this.dataset.id;
    const isRead = this.dataset.read === 'true';
    const boardId = this.dataset.boardId;
    
    if (!isRead && id) {
        markNotificationAsRead(id);
    }
    
    // Cerrar dropdown de Bootstrap 5
    const bell = document.getElementById('notificationsBell');
    if (bell) {
        const dropdown = bootstrap.Dropdown.getInstance(bell);
        if (dropdown) dropdown.hide();
    }
    
    // Redirigir si hay un tablero asociado
    if (boardId) {
        window.location.href = `/boards/${boardId}/`;
    }
}

function getIconClass(type) {
    const icons = {
        'task_assigned': 'fas fa-user-plus',
        'comment_added': 'fas fa-comment',
        'task_moved': 'fas fa-arrows-alt',
        'mention': 'fas fa-at',
        'member_added': 'fas fa-user-friends'
    };
    return icons[type] || 'fas fa-bell';
}

function getIconColor(type) {
    const colors = {
        'task_assigned': 'bg-success bg-opacity-10 text-success',
        'comment_added': 'bg-primary bg-opacity-10 text-primary',
        'task_moved': 'bg-warning bg-opacity-10 text-warning',
        'mention': 'bg-info bg-opacity-10 text-info',
        'member_added': 'bg-secondary bg-opacity-10 text-secondary'
    };
    return colors[type] || 'bg-light text-secondary';
}

function formatTime(isoString) {
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffMins < 1) return 'Hace unos segundos';
    if (diffMins < 60) return `Hace ${diffMins} minuto${diffMins !== 1 ? 's' : ''}`;
    if (diffHours < 24) return `Hace ${diffHours} hora${diffHours !== 1 ? 's' : ''}`;
    if (diffDays < 7) return `Hace ${diffDays} día${diffDays !== 1 ? 's' : ''}`;
    
    return date.toLocaleDateString('es-ES', { day: 'numeric', month: 'short' });
}

function updateNotificationBadge(count) {
    const badge = document.getElementById('notifications-badge');
    if (!badge) return;
    
    if (count > 0) {
        badge.textContent = count > 99 ? '99+' : count;
        badge.style.display = 'inline-block';
    } else {
        badge.style.display = 'none';
    }
}

function markNotificationAsRead(id) {
    fetch(`/notifications/api/mark/${id}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(() => {
        loadNotifications();
        updateGlobalUnreadCount();
    })
    .catch(error => console.error('Error:', error));
}

function markAllNotificationsAsRead() {
    fetch('/notifications/api/mark-all/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(() => {
        loadNotifications();
        updateNotificationBadge(0);
    })
    .catch(error => console.error('Error:', error));
}

function updateGlobalUnreadCount() {
    fetch('/notifications/api/get/?limit=1')
        .then(response => response.json())
        .then(data => {
            updateNotificationBadge(data.unread_count);
        })
        .catch(error => console.error('Error:', error));
}

function getCsrfToken() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') return value;
    }
    return '';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ========== WEBSOCKET EN TIEMPO REAL ==========

function initNotificationsWebSocket() {
    const wsScheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const wsUrl = `${wsScheme}://${window.location.host}/ws/notifications/`;
    
    notificationsWebSocket = new WebSocket(wsUrl);
    
    notificationsWebSocket.onopen = function() {
        console.log('✅ WebSocket notificaciones conectado');
    };
    
    notificationsWebSocket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        console.log('📨 Nueva notificación en tiempo real:', data);
        
        if (data.type === 'notification') {
            // 1. Agrega el item al dropdown de la campana (esté abierto o cerrado)
            addNotificationToDropdown(data.notification);
            
            // 2. Incrementa el número del badge
            updateBadgeAfterNewNotification();
            
            // 3. 🔥 NUEVO: Muestra un aviso flotante en pantalla
            mostrarAlertaFlotante(data.notification);
            
            // 4. 🔥 NUEVO: Si estás en el tablero correcto, dibuja la tarjeta en vivo
            if (typeof renderizarTarjetaEnVivo === 'function') {
                renderizarTarjetaEnVivo(data.notification);
            }
        }
    };
    
    notificationsWebSocket.onerror = function(error) {
        console.error('❌ WebSocket error:', error);
    };
    
    notificationsWebSocket.onclose = function() {
        console.log('🔌 WebSocket notificaciones desconectado');
        setTimeout(initNotificationsWebSocket, 5000);
    };
}

// 🔥 FUNCIÓN NUEVA: Alerta flotante temporal
function mostrarAlertaFlotante(notification) {
    // Verificamos si existe un contenedor para toasts, si no, lo creamos dinámicamente
    let container = document.getElementById('toast-container-custom');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container-custom';
        container.style.position = 'fixed';
        container.style.bottom = '20px';
        container.style.right = '20px';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = 'toast-alert-realtime';
    toast.style.background = '#333';
    toast.style.color = '#fff';
    toast.style.padding = '15px 20px';
    toast.style.borderRadius = '8px';
    toast.style.marginBottom = '10px';
    toast.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
    toast.style.display = 'flex';
    toast.style.alignItems = 'center';
    toast.style.gap = '10px';
    toast.style.animation = 'slideIn 0.3s ease forwards';

    toast.innerHTML = `
        <div style="font-size: 1.2rem;"><i class="${getIconClass(notification.type)}"></i></div>
        <div>
            <strong style="display:block; font-size: 0.9rem;">Nueva notificación</strong>
            <span style="font-size: 0.85rem; color: #ccc;">${escapeHtml(notification.message)}</span>
        </div>
    `;

    container.appendChild(toast);

    // Desaparecer automáticamente a los 5 segundos
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease forwards';
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

function addNotificationToDropdown(notification) {
    const container = document.getElementById('notifications-list');
    
    if (container) {
        // Quitar el mensaje de lista vacía si existe
        const emptyMsg = container.querySelector('.empty-notifications');
        if (emptyMsg) emptyMsg.remove();

        const newItem = document.createElement('div');
        newItem.className = 'notification-item unread';
        newItem.setAttribute('data-id', notification.id);
        newItem.setAttribute('data-read', 'false');
        newItem.setAttribute('data-board-id', notification.board_id || '');
        newItem.setAttribute('data-card-id', notification.card_id || '');
        newItem.innerHTML = `
            <div class="notification-icon-custom ${getIconColor(notification.type)}">
                <i class="${getIconClass(notification.type)}"></i>
            </div>
            <div class="notification-content">
                <div class="notification-message">${escapeHtml(notification.message)}</div>
                <div class="notification-time">Ahora mismo</div>
            </div>
            <div class="notification-badge-unread"></div>
        `;
        
        // 💡 Inserción limpia e incondicional al principio del contenedor
        if (container.firstChild) {
            container.insertBefore(newItem, container.firstChild);
        } else {
            container.appendChild(newItem);
        }
        
        // Volver a enlazar el evento clic para que el nuevo item sea interactivo
        setupNotificationClickEvents();
    }
    
    playNotificationSound();
}

function updateBadgeAfterNewNotification() {
    const badge = document.getElementById('notifications-badge');
    if (!badge) return;
    
    let current = parseInt(badge.textContent) || 0;
    let newCount = current + 1;
    badge.textContent = newCount > 99 ? '99+' : newCount;
    badge.style.display = 'inline-block';
}

function playNotificationSound() {
    try {
        const audio = new Audio('/static/sounds/notification.mp3');
        audio.volume = 0.3;
        audio.play().catch(e => console.log('Sonido no disponible por políticas del navegador'));
    } catch(e) {
        console.log('Audio no soportado');
    }
}

// Cargar notificaciones iniciales al cargar la página
setTimeout(() => {
    loadNotifications();
}, 500);