/**
 * Lógica global para el sistema de contactos (estilo solicitudes de amistad).
 * Estas funciones son globales (no encapsuladas en un IIFE) porque se
 * invocan desde atributos onclick generados dinámicamente en varias partes
 * de la app: el dropdown de búsqueda en tiempo real, la página de resultados
 * de búsqueda, el panel de notificaciones, el icono de solicitudes de
 * contacto en la barra de navegación y la página "Mis Contactos".
 */

/**
 * Envía una solicitud de contacto a otro usuario.
 * @param {number} userId - ID del usuario destino.
 * @param {HTMLElement} [btn] - Botón que disparó la acción (opcional, para feedback visual).
 */
async function sendContactRequest(userId, btn) {
    if (btn) {
        btn.disabled = true;
        btn.dataset.originalHtml = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    }

    try {
        const response = await fetch('/api/contacts/send-request/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': FlowTaskHelpers.getCSRFToken(),
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin',
            body: JSON.stringify({ user_id: userId }),
        });

        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
            throw new Error(data.detail || 'No se pudo enviar la solicitud.');
        }

        if (btn) {
            const badge = document.createElement('span');
            badge.className = 'badge bg-warning text-dark';
            badge.style.cssText = 'font-size: 0.75rem; padding: 0.25rem 0.5rem; border-radius: var(--radius-sm);';
            badge.textContent = 'Enviada';
            btn.replaceWith(badge);
        }

        FlowTaskHelpers.showToast(data.detail || 'Solicitud enviada correctamente.', 'success');
    } catch (error) {
        console.error('Error enviando solicitud de contacto:', error);
        FlowTaskHelpers.showToast(error.message || 'Ocurrió un error inesperado.', 'error');
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = btn.dataset.originalHtml || '<i class="fas fa-user-plus"></i> Añadir';
        }
    }
}

/**
 * Responde (acepta o rechaza) una solicitud de contacto pendiente.
 * @param {number} userId - ID del usuario que envió la solicitud.
 * @param {string} action - 'accept' o 'reject'.
 * @param {HTMLElement} [btn] - Botón que disparó la acción (opcional).
 */
async function respondContactRequest(userId, action, btn) {
    const actionContainer = btn ? (btn.closest('.user-action-btn') || btn.closest('.d-flex') || btn.parentElement) : null;

    if (btn) btn.disabled = true;

    try {
        const response = await fetch('/api/contacts/respond-request/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': FlowTaskHelpers.getCSRFToken(),
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin',
            body: JSON.stringify({ user_id: userId, action: action }),
        });

        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
            throw new Error(data.detail || 'No se pudo procesar la respuesta.');
        }

        if (actionContainer) {
            if (action === 'accept') {
                actionContainer.innerHTML = '<span class="badge bg-success">Contacto</span>';
            } else {
                actionContainer.innerHTML = '<span class="badge bg-secondary">Rechazada</span>';
            }
        } else if (btn) {
            btn.remove();
        }

        // Quitamos esta solicitud de cualquier lugar donde aparezca pendiente:
        // el icono dedicado de solicitudes de contacto y el panel de notificaciones.
        document.querySelectorAll(`.contact-request-item[data-sender-id="${userId}"]`).forEach(el => el.remove());
        document.querySelectorAll(`.notification-actions[data-sender-id="${userId}"]`).forEach(el => el.remove());

        if (window.FlowTaskContactRequests) {
            window.FlowTaskContactRequests.decrementBadge();
        }

        FlowTaskHelpers.showToast(
            data.detail || (action === 'accept' ? 'Ahora son contactos.' : 'Solicitud rechazada.'),
            'success'
        );
    } catch (error) {
        console.error('Error respondiendo solicitud de contacto:', error);
        FlowTaskHelpers.showToast(error.message || 'Ocurrió un error al procesar la solicitud.', 'error');
        if (btn) btn.disabled = false;
    }
}

/**
 * Elimina un contacto ya aceptado.
 * @param {number} userId - ID del contacto a eliminar.
 * @param {HTMLElement} [btn] - Botón que disparó la acción (opcional).
 */
async function removeContact(userId, btn) {
    if (!confirm('¿Seguro que querés eliminar este contacto?')) return;

    if (btn) btn.disabled = true;

    try {
        const response = await fetch('/api/contacts/remove-contact/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': FlowTaskHelpers.getCSRFToken(),
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin',
            body: JSON.stringify({ user_id: userId }),
        });

        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
            throw new Error(data.detail || 'No se pudo eliminar el contacto.');
        }

        const card = document.querySelector(`.contact-card[data-user-id="${userId}"]`);
        if (card) {
            card.remove();
        }

        const list = document.getElementById('contactsList');
        if (list && !list.querySelector('.contact-card')) {
            list.innerHTML = `
                <div class="empty-state" id="contactsEmptyState">
                    <i class="fas fa-address-book"></i>
                    <p>Todavía no tenés contactos agregados.</p>
                </div>
            `;
        }

        FlowTaskHelpers.showToast('Contacto eliminado correctamente.', 'success');
    } catch (error) {
        console.error('Error eliminando contacto:', error);
        FlowTaskHelpers.showToast(error.message || 'Ocurrió un error inesperado.', 'error');
        if (btn) btn.disabled = false;
    }
}
