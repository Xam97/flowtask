// static/js/contact_requests.js
// Icono dedicado de solicitudes de contacto (separado de la campana de notificaciones).
// Solo desaparece un ítem de este panel una vez que el usuario responde (acepta o rechaza).

(function() {
    'use strict';

    let loaded = false;

    document.addEventListener('DOMContentLoaded', () => {
        const panel = document.getElementById('contactRequestsPanel');
        const toggle = document.getElementById('contactRequestsToggle');
        if (!panel || !toggle) return;

        loadPendingRequests();

        toggle.addEventListener('click', (e) => {
            e.preventDefault();
            panel.classList.toggle('show');
            if (!loaded) loadPendingRequests();
        });

        document.addEventListener('click', (e) => {
            if (!e.target.closest('.contact-requests-wrapper')) {
                panel.classList.remove('show');
            }
        });

        // Actualización en tiempo real cuando llega una nueva solicitud por WebSocket.
        if (window.FlowTaskWebSocket) {
            FlowTaskWebSocket.on('onNotification', (data) => {
                if (data.type === 'contact_request') {
                    loadPendingRequests();
                }
            });
        }
    });

    async function loadPendingRequests() {
        try {
            const response = await fetch('/api/contacts/pending-requests/', { credentials: 'same-origin' });
            if (!response.ok) return;
            const data = await response.json();
            renderRequests(data.results || []);
            updateBadge(data.count || 0);
            loaded = true;
        } catch (error) {
            console.error('Error cargando solicitudes de contacto:', error);
        }
    }

    function renderRequests(requests) {
        const list = document.getElementById('contactRequestsList');
        if (!list) return;

        if (!requests.length) {
            list.innerHTML = '<li class="notification-empty">No tenés solicitudes pendientes</li>';
            return;
        }

        list.innerHTML = requests.map(buildRequestItemHTML).join('');
    }

    function buildRequestItemHTML(r) {
        const fullName = `${r.first_name || ''} ${r.last_name || ''}`.trim();
        return `
            <li class="notification-item contact-request-item" data-sender-id="${r.id}">
                <div class="notification-link" style="cursor:default;">
                    <span class="notification-icon-type member"><i class="fas fa-user"></i></span>
                    <div class="notification-content">
                        <strong>${FlowTaskHelpers.escapeHtml(r.username)}</strong>
                        <p>${FlowTaskHelpers.escapeHtml(fullName || 'Quiere agregarte como contacto')}</p>
                        <small><i class="fas fa-clock"></i> ${r.created_at}</small>
                        <div class="d-flex gap-2 mt-2">
                            <button class="btn btn-sm btn-success py-0 px-2" style="font-size: 0.75rem;" onclick="respondContactRequest(${r.id}, 'accept', this)">
                                Aceptar
                            </button>
                            <button class="btn btn-sm btn-danger py-0 px-2" style="font-size: 0.75rem;" onclick="respondContactRequest(${r.id}, 'reject', this)">
                                Rechazar
                            </button>
                        </div>
                    </div>
                </div>
            </li>
        `;
    }

    function updateBadge(count) {
        const badge = document.getElementById('contactRequestsBadge');
        if (!badge) return;
        badge.textContent = count;
        badge.style.display = count > 0 ? 'inline-flex' : 'none';
    }

    function decrementBadge() {
        const badge = document.getElementById('contactRequestsBadge');
        if (!badge) return;
        const current = Math.max(0, (parseInt(badge.textContent) || 1) - 1);
        updateBadge(current);

        const list = document.getElementById('contactRequestsList');
        if (list && !list.querySelector('.contact-request-item')) {
            list.innerHTML = '<li class="notification-empty">No tenés solicitudes pendientes</li>';
        }
    }

    // API pública usada por search_contacts.js al responder una solicitud.
    window.FlowTaskContactRequests = {
        refresh: loadPendingRequests,
        decrementBadge: decrementBadge,
    };
})();
