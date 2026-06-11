// Panel de notificaciones en tiempo real

(function() {
    'use strict';

    let notificationsLoaded = false;

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

        document.addEventListener('click', (e) => {
            if (!e.target.closest('.notification-wrapper')) {
                panel.classList.remove('show');
            }
        });
    });

    async function loadNotifications() {
        try {
            const response = await fetch('/notifications/', { credentials: 'same-origin' });
            const data = await response.json();
            if (data.success) {
                renderNotifications(data.notifications);
                updateBadge(data.unread_count);
                notificationsLoaded = true;
            }
        } catch (error) {
            console.error('Error cargando notificaciones:', error);
        }
    }

    function renderNotifications(notifications) {
        const list = document.getElementById('notificationList');
        if (!list) return;

        if (!notifications.length) {
            list.innerHTML = '<li class="notification-empty">No tienes notificaciones</li>';
            return;
        }

        list.innerHTML = notifications.map(n => `
            <li class="notification-item ${n.is_read ? '' : 'unread'}" data-id="${n.id}">
                <a href="${getNotificationLink(n)}" class="notification-link">
                    <span class="notification-icon-type">${getTypeIcon(n.type)}</span>
                    <div class="notification-content">
                        <strong>${FlowTaskHelpers.escapeHtml(n.title)}</strong>
                        <p>${FlowTaskHelpers.escapeHtml(n.message)}</p>
                        <small>${n.created_at}</small>
                    </div>
                </a>
            </li>
        `).join('');

        list.querySelectorAll('.notification-item.unread').forEach(item => {
            item.addEventListener('click', () => markAsRead(item.dataset.id));
        });
    }

    function getNotificationLink(n) {
        if (n.board_id) return `/boards/${n.board_id}/`;
        return '#';
    }

    function getTypeIcon(type) {
        const icons = {
            card_assigned: '<i class="fas fa-user-check"></i>',
            new_comment: '<i class="fas fa-comment"></i>',
            member_added: '<i class="fas fa-users"></i>',
            card_moved: '<i class="fas fa-arrows-alt"></i>',
            card_deleted: '<i class="fas fa-trash"></i>',
        };
        return icons[type] || '<i class="fas fa-bell"></i>';
    }

    function handleNewNotification(data) {
        const list = document.getElementById('notificationList');
        if (list) {
            const empty = list.querySelector('.notification-empty');
            if (empty) empty.remove();

            const item = document.createElement('li');
            item.className = 'notification-item unread';
            item.dataset.id = data.id;
            item.innerHTML = `
                <a href="${getNotificationLink(data)}" class="notification-link">
                    <span class="notification-icon-type">${getTypeIcon(data.type)}</span>
                    <div class="notification-content">
                        <strong>${FlowTaskHelpers.escapeHtml(data.title)}</strong>
                        <p>${FlowTaskHelpers.escapeHtml(data.message)}</p>
                        <small>${data.created_at}</small>
                    </div>
                </a>
            `;
            list.prepend(item);
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

    async function markAsRead(id) {
        try {
            await fetch(`/notifications/${id}/read/`, {
                method: 'POST',
                headers: { 'X-CSRFToken': FlowTaskHelpers.getCSRFToken() },
                credentials: 'same-origin',
            });
            const item = document.querySelector(`.notification-item[data-id="${id}"]`);
            if (item) item.classList.remove('unread');
            const response = await fetch('/notifications/unread-count/', { credentials: 'same-origin' });
            const data = await response.json();
            updateBadge(data.unread_count);
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
            document.querySelectorAll('.notification-item.unread').forEach(el => el.classList.remove('unread'));
            updateBadge(data.unread_count);
        } catch (error) {
            console.error('Error:', error);
        }
    }
})();
