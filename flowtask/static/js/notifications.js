// Panel de notificaciones en tiempo real

(function() {
    'use strict';

    let notificationsLoaded = false;
    let currentPage = 1;

    document.addEventListener('DOMContentLoaded', () => {
        const panel = document.getElementById('notificationPanel');
        if (!panel) return;

        loadNotifications();
        FlowTaskWebSocket.connectToNotifications();
        FlowTaskWebSocket.on('onNotification', handleNewNotification);

        const toggle = document.getElementById('notificationToggle');
        if (toggle) {
            toggle.addEventListener('click', (e) => {
                e.preventDefault();
                panel.classList.toggle('show');
                if (!notificationsLoaded) loadNotifications();
            });
        }

        document.getElementById('markAllReadBtn')?.addEventListener('click', markAllRead);
        document.getElementById('deleteReadBtn')?.addEventListener('click', deleteAllRead);

        document.addEventListener('click', (e) => {
            if (!e.target.closest('.notification-wrapper')) {
                panel.classList.remove('show');
            }
            const deleteBtn = e.target.closest('.notification-delete-btn');
            if (deleteBtn) {
                e.preventDefault();
                e.stopPropagation();
                deleteNotification(deleteBtn.dataset.id);
            }
        });
    });

    async function loadNotifications(page = 1) {
        try {
            const response = await fetch(`/notifications/?page=${page}&limit=30`, { credentials: 'same-origin' });
            const data = await response.json();
            if (data.success) {
                renderNotifications(data.notifications, data.has_more);
                updateBadge(data.unread_count);
                notificationsLoaded = true;
                currentPage = page;
            }
        } catch (error) {
            console.error('Error cargando notificaciones:', error);
        }
    }

    // Generador de estructura para cada fila (reutilizable en render e hilos websocket)
    function buildNotificationHTML(n) {
        const isUnread = n.is_read ? '' : 'unread';
        const formattedDate = formatDate(n.created_at);

        let actionButtons = '';
        // 💡 Si es una solicitud de contacto y viene de backend con estado pendiente
        if (n.type === 'contact_request' && n.request_status === 'pending') {
            actionButtons = `
                <div class="notification-actions mt-2 d-flex gap-2" data-sender-id="${n.sender_id}" style="padding-left: 2.25rem;">
                    <button class="btn btn-sm btn-success py-0 px-2" style="font-size: 0.75rem;" 
                            onclick="respondContactRequest(${n.sender_id}, 'accept', this)">
                        Aceptar
                    </button>
                    <button class="btn btn-sm btn-danger py-0 px-2" style="font-size: 0.75rem;" 
                            onclick="respondContactRequest(${n.sender_id}, 'reject', this)">
                        Rechazar
                    </button>
                </div>
            `;
        }

        return `
            <li class="notification-item ${isUnread}" data-id="${n.id}">
                <a href="${getNotificationLink(n)}" class="notification-link">
                    <span class="notification-icon-type">${getTypeIcon(n.type)}</span>
                    <div class="notification-content">
                        <strong>${FlowTaskHelpers.escapeHtml(n.title)}</strong>
                        <p>${FlowTaskHelpers.escapeHtml(n.message)}</p>
                        <small>${formattedDate}</small>
                    </div>
                </a>
                <button class="notification-delete-btn" data-id="${n.id}" title="Eliminar">
                    <i class="fas fa-times"></i>
                </button>
                ${actionButtons}
            </li>
        `;
    }

    function renderNotifications(notifications, hasMore) {
        const list = document.getElementById('notificationList');
        if (!list) return;

        if (!notifications.length) {
            list.innerHTML = '<li class="notification-empty">No tienes notificaciones</li>';
            return;
        }

        list.innerHTML = notifications.map(n => buildNotificationHTML(n)).join('');

        if (hasMore) {
            const loadMore = document.createElement('li');
            loadMore.className = 'notification-load-more';
            loadMore.innerHTML = `<button class="btn btn-sm btn-link w-100" id="loadMoreNotifications">Cargar más</button>`;
            list.appendChild(loadMore);
            document.getElementById('loadMoreNotifications')?.addEventListener('click', () => {
                loadNotifications(currentPage + 1);
            });
        }

        list.querySelectorAll('.notification-item.unread .notification-link').forEach(link => {
            link.addEventListener('click', () => markAsRead(link.closest('.notification-item').dataset.id));
        });
    }

    function getNotificationLink(n) {
        if (n.board_id) return `/boards/${n.board_id}/`;
        if (n.type === 'contact_request' || n.type === 'contact_accepted') return '/boards/contacts/';
        return '#';
    }

    function getTypeIcon(type) {
        const icons = {
            card_assigned: '<i class="fas fa-user-check"></i>',
            new_comment: '<i class="fas fa-comment"></i>',
            member_added: '<i class="fas fa-users"></i>',
            card_moved: '<i class="fas fa-arrows-alt"></i>',
            card_deleted: '<i class="fas fa-trash"></i>',
            contact_request: '<i class="fas fa-user-plus text-primary"></i>',
            contact_accepted: '<i class="fas fa-user-check text-success"></i>',
        };
        return icons[type] || '<i class="fas fa-bell"></i>';
    }

    function handleNewNotification(data) {
        const list = document.getElementById('notificationList');
        if (list) {
            const empty = list.querySelector('.notification-empty');
            if (empty) empty.remove();

            const itemHTML = buildNotificationHTML(data);
            list.insertAdjacentHTML('afterbegin', itemHTML);

            const insertedItem = list.querySelector(`.notification-item[data-id="${data.id}"]`);
            insertedItem.querySelector('.notification-link').addEventListener('click', () => markAsRead(data.id));
        }

        const badge = document.getElementById('notificationBadge');
        if (badge) {
            const count = (parseInt(badge.textContent) || 0) + 1;
            badge.textContent = count;
            badge.style.display = count > 0 ? 'inline-flex' : 'none';
        }
    }

    function updateBadge(count) {
        const badge = document.getElementById('notificationBadge');
        if (!badge) return;
        badge.textContent = count;
        badge.style.display = count > 0 ? 'inline-flex' : 'none';
    }

    function formatDate(isoString) {
        if (!isoString) return '';
        const date = new Date(isoString);
        return date.toLocaleDateString('es-PY', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });
    }

    async function markAsRead(id) {
        try {
            const response = await fetch(`/notifications/${id}/read/`, {
                method: 'POST',
                headers: { 'X-CSRFToken': FlowTaskHelpers.getCSRFToken() },
                credentials: 'same-origin',
            });
            const data = await response.json();
            
            if (data.success) {
                const item = document.querySelector(`.notification-item[data-id="${id}"]`);
                if (item && item.classList.contains('unread')) {
                    item.classList.remove('unread');
                    
                    const badge = document.getElementById('notificationBadge');
                    if (badge) {
                        const currentCount = Math.max(0, (parseInt(badge.textContent) || 0) - 1);
                        updateBadge(currentCount);
                    }
                }
            }
        } catch (error) {
            console.error('Error marcando notificación:', error);
        }
    }

    async function markAllRead() {
        try {
            const response = await fetch('/notifications/mark-all-read/', {
                method: 'POST',
                headers: { 'X-CSRFToken': FlowTaskHelpers.getCSRFToken() },
                credentials: 'same-origin',
            });
            const data = await response.json();

            if (data.success) {
                document.querySelectorAll('.notification-item.unread').forEach(el => el.classList.remove('unread'));
                updateBadge(0);
            }
        } catch (error) {
            console.error('Error:', error);
        }
    }

    async function deleteNotification(id) {
        try {
            const response = await fetch(`/notifications/${id}/delete/`, {
                method: 'POST',
                headers: { 'X-CSRFToken': FlowTaskHelpers.getCSRFToken() },
                credentials: 'same-origin',
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                document.querySelector(`.notification-item[data-id="${id}"]`)?.remove();
                updateBadge(data.unread_count);
            } else {
                FlowTaskHelpers.showToast(data.error || 'No se puede eliminar', 'error');
            }
        } catch (error) {
            console.error('Error eliminando notificación:', error);
        }
    }

    async function deleteAllRead() {
        try {
            const response = await fetch('/notifications/delete-read/', {
                method: 'POST',
                headers: { 'X-CSRFToken': FlowTaskHelpers.getCSRFToken() },
                credentials: 'same-origin',
            });
            const data = await response.json();
            loadNotifications();
            updateBadge(data.unread_count);
            FlowTaskHelpers.showToast(`${data.deleted_count} notificaciones procesadas`, 'success');
        } catch (error) {
            console.error('Error:', error);
        }
    }
})();