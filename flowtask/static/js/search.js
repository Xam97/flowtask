// Global search with live dropdown
(function() {
    'use strict';

    document.addEventListener('DOMContentLoaded', () => {
        const input = document.getElementById('globalSearchInput');
        const dropdown = document.getElementById('searchDropdown');
        const form = document.getElementById('globalSearchForm');

        if (!input || !dropdown) return;

        const debouncedSearch = FlowTaskHelpers.debounce(async (query) => {
            if (query.length < 2) {
                dropdown.classList.remove('show');
                return;
            }

            try {
                // Ejecutamos ambas búsquedas en paralelo usando Promise.all
                const [workspaceResponse, contactsResponse] = await Promise.all([
                    fetch(`/boards/search/api/?q=${encodeURIComponent(query)}`, { credentials: 'same-origin' }),
                    fetch(`/api/contacts/search/?q=${encodeURIComponent(query)}`, { credentials: 'same-origin' })
                ]);

                const workspaceData = await workspaceResponse.json();
                const contactsData = await contactsResponse.json();

                // Unificamos el renderizado pasando ambos resultados
                renderResults(workspaceData, contactsData, query);
            } catch (e) {
                console.error('Search error:', e);
            }
        }, 300);

        input.addEventListener('input', () => debouncedSearch(input.value.trim()));
        input.addEventListener('focus', () => {
            if (input.value.trim().length >= 2) debouncedSearch(input.value.trim());
        });

        document.addEventListener('click', (e) => {
            if (!e.target.closest('.search-wrapper')) {
                dropdown.classList.remove('show');
            }
        });

        form.addEventListener('submit', (e) => {
            if (input.value.trim().length < 2) {
                e.preventDefault();
                FlowTaskHelpers.showToast('Escribe al menos 2 caracteres', 'error');
            }
        });
    });

    function renderResults(workspaceData, users, query) {
        const dropdown = document.getElementById('searchDropdown');
        if (!dropdown) return;

        const boards = workspaceData.boards || [];
        const cards = workspaceData.cards || [];

        // Validamos si absolutamente todo vino vacío
        if (boards.length === 0 && cards.length === 0 && (!users || users.length === 0)) {
            dropdown.innerHTML = `<div class="search-empty">Sin resultados para "${FlowTaskHelpers.escapeHtml(query)}"</div>`;
            dropdown.classList.add('show');
            return;
        }

        let html = '';

        // ================= SECCIÓN: USUARIOS =================
        if (users && users.length > 0) {
            html += '<div class="search-dropdown-section"><h6>Usuarios</h6>';
            users.forEach(user => {
                let buttonHTML = '';
                
                // Mapeo dinámico de botones según el estado calculado en DRF
                if (user.contact_status === 'none') {
                    buttonHTML = `<button class="btn btn-sm btn-primary" style="padding: 2px 8px; font-size: 0.75rem;" onclick="sendContactRequest(${user.id}, this)">Añadir</button>`;
                } else if (user.contact_status === 'pending_sent') {
                    buttonHTML = `<span class="badge bg-warning text-dark" style="font-size: 0.7rem;">Enviada</span>`;
                } else if (user.contact_status === 'pending_received') {
                    buttonHTML = `
                        <div class="d-flex gap-1">
                            <button class="btn btn-sm btn-success" style="padding: 2px 8px; font-size: 0.75rem;" onclick="respondContactRequest(${user.id}, 'accept', this)">Aceptar</button>
                            <button class="btn btn-sm btn-danger" style="padding: 2px 8px; font-size: 0.75rem;" onclick="respondContactRequest(${user.id}, 'reject', this)">Rechazar</button>
                        </div>
                    `;
                } else if (user.contact_status === 'accepted') {
                    buttonHTML = `<span class="badge bg-success" style="font-size: 0.7rem;">Contacto</span>`;
                }

                html += `
                    <div class="search-result-item" style="display: flex; justify-content: space-between; align-items: center; cursor: default;" data-user-id="${user.id}">
                        <div style="display: flex; align-items: center;">
                            <div class="search-result-icon" style="background: var(--primary-light, #e9ecef); color: var(--primary, #007bff);"><i class="fas fa-user"></i></div>
                            <div class="search-result-text">
                                <strong>${FlowTaskHelpers.escapeHtml(user.username)}</strong>
                                <small>${FlowTaskHelpers.escapeHtml(user.first_name || '')} ${FlowTaskHelpers.escapeHtml(user.last_name || '')}</small>
                            </div>
                        </div>
                        <div class="user-action-btn" style="margin-left: 10px;">
                            ${buttonHTML}
                        </div>
                    </div>
                `;
            });
            html += '</div>';
        }

        // ================= SECCIÓN: TABLEROS =================
        if (boards.length) {
            html += '<div class="search-dropdown-section"><h6>Tableros</h6>';
            boards.forEach(b => {
                html += `<a href="${b.url}" class="search-result-item">
                    <div class="search-result-icon board"><i class="fas fa-th-large"></i></div>
                    <div class="search-result-text"><strong>${FlowTaskHelpers.escapeHtml(b.name)}</strong></div>
                </a>`;
            });
            html += '</div>';
        }

        // ================= SECCIÓN: TAREAS =================
        if (cards.length) {
            html += '<div class="search-dropdown-section"><h6>Tareas</h6>';
            cards.forEach(c => {
                html += `<a href="${c.url}" class="search-result-item">
                    <div class="search-result-icon card"><i class="fas fa-tasks"></i></div>
                    <div class="search-result-text">
                        <strong>${FlowTaskHelpers.escapeHtml(c.title)}</strong>
                        <small>${FlowTaskHelpers.escapeHtml(c.board_name)} · ${FlowTaskHelpers.escapeHtml(c.list_name)}</small>
                    </div>
                </a>`;
            });
            html += '</div>';
        }

        // Pie del dropdown (Ver todos)
        html += `<div class="search-dropdown-section" style="padding:0.5rem;text-align:center;">
            <a href="/boards/search/?q=${encodeURIComponent(query)}" style="font-size:0.75rem;color:var(--accent);">Ver todos los resultados</a>
        </div>`;

        dropdown.innerHTML = html;
        dropdown.classList.add('show');
    }
})();