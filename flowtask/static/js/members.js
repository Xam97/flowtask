// Gestión de miembros y permisos del tablero

(function() {
    'use strict';

    document.addEventListener('DOMContentLoaded', () => {
        const modal = document.getElementById('manageMembersModal');
        if (modal) {
            modal.addEventListener('show.bs.modal', loadMembers);

            modal.addEventListener('click', async (e) => {
                const saveBtn = e.target.closest('.save-permissions-btn');
                const removeBtn = e.target.closest('.remove-member-btn');
                if (saveBtn) await savePermissions(saveBtn);
                if (removeBtn) await removeMember(removeBtn);
            });
        }

        initInviteAutocomplete();
    });

    // ================= AUTOCOMPLETADO DE INVITACIÓN =================

    function initInviteAutocomplete() {
        const input = document.getElementById('inviteUsernameInput');
        const hidden = document.getElementById('inviteUsernameHidden');
        const suggestionsBox = document.getElementById('inviteSuggestions');
        const submitBtn = document.getElementById('inviteSubmitBtn');
        const addMemberModal = document.getElementById('addMemberModal');
        if (!input || !hidden || !suggestionsBox || !submitBtn || !addMemberModal) return;

        const boardId = document.querySelector('.kanban-container')?.dataset.boardId;
        let debounceTimer = null;
        let currentResults = [];

        function invalidateSelection() {
            hidden.value = '';
            submitBtn.disabled = true;
        }

        input.addEventListener('input', () => {
            invalidateSelection();
            const query = input.value.trim();

            clearTimeout(debounceTimer);
            if (query.length < 2) {
                suggestionsBox.classList.remove('show');
                suggestionsBox.innerHTML = '';
                return;
            }

            debounceTimer = setTimeout(() => fetchSuggestions(query), 250);
        });

        async function fetchSuggestions(query) {
            try {
                const response = await fetch(
                    `/boards/${boardId}/members/search-invite/?q=${encodeURIComponent(query)}`,
                    { credentials: 'same-origin' }
                );
                const data = await response.json();
                currentResults = data.results || [];
                renderSuggestions(currentResults);
            } catch (error) {
                console.error('Error buscando usuarios para invitar:', error);
            }
        }

        function renderSuggestions(results) {
            if (!results.length) {
                suggestionsBox.innerHTML = '<div class="invite-suggestion-empty">Sin coincidencias</div>';
                suggestionsBox.classList.add('show');
                return;
            }

            suggestionsBox.innerHTML = results.map(u => {
                const fullName = `${u.first_name || ''} ${u.last_name || ''}`.trim();
                return `
                    <div class="invite-suggestion-item" data-id="${u.id}" data-username="${FlowTaskHelpers.escapeHtml(u.username)}">
                        <span class="invite-suggestion-avatar">${u.username.charAt(0).toUpperCase()}</span>
                        <div>
                            <strong>${FlowTaskHelpers.escapeHtml(u.username)}</strong>
                            ${fullName ? `<small>${FlowTaskHelpers.escapeHtml(fullName)}</small>` : ''}
                        </div>
                    </div>
                `;
            }).join('');
            suggestionsBox.classList.add('show');
        }

        suggestionsBox.addEventListener('click', (e) => {
            const item = e.target.closest('.invite-suggestion-item');
            if (!item) return;

            input.value = item.dataset.username;
            hidden.value = item.dataset.username;
            submitBtn.disabled = false;
            suggestionsBox.classList.remove('show');
            suggestionsBox.innerHTML = '';
        });

        document.addEventListener('click', (e) => {
            if (!e.target.closest('.invite-autocomplete-wrapper')) {
                suggestionsBox.classList.remove('show');
            }
        });

        // Reseteamos el formulario cada vez que se abre el modal para
        // evitar que quede una selección vieja de una invitación anterior.
        addMemberModal.addEventListener('show.bs.modal', () => {
            input.value = '';
            hidden.value = '';
            submitBtn.disabled = true;
            suggestionsBox.classList.remove('show');
            suggestionsBox.innerHTML = '';
        });
    }

    async function loadMembers() {
        const container = document.getElementById('membersManagementList');
        const boardId = document.querySelector('.kanban-container')?.dataset.boardId;
        if (!container || !boardId) return;

        container.innerHTML = '<div class="text-center py-3"><i class="fas fa-spinner fa-spin"></i> Cargando...</div>';

        try {
            const response = await fetch(`/boards/${boardId}/members/`, { credentials: 'same-origin' });
            const data = await response.json();
            if (!data.success) throw new Error(data.error || 'Error');

            let html = `
                <div class="member-mgmt-row owner-row mb-3 p-3 rounded">
                    <div class="d-flex align-items-center gap-2">
                        <span class="member-avatar">${data.owner.username.charAt(0).toUpperCase()}</span>
                        <strong>${FlowTaskHelpers.escapeHtml(data.owner.username)}</strong>
                        <span class="badge bg-warning text-dark"><i class="fas fa-crown"></i> Creador</span>
                    </div>
                </div>
            `;

            if (!data.members.length) {
                html += '<p class="text-muted">No hay otros miembros en este tablero.</p>';
            }

            data.members.forEach(m => {
                html += renderMemberRow(m, data.can_manage);
            });

            container.innerHTML = html;
        } catch (error) {
            container.innerHTML = `<div class="alert alert-danger">${error.message}</div>`;
        }
    }

    function renderMemberRow(member, canManage) {
        const permsHtml = member.role === 'member' ? `
            <div class="grantable-perms mt-2">
                <small class="text-muted d-block mb-1">Permisos adicionales:</small>
                <div class="d-flex flex-wrap gap-3">
                    ${permCheckbox(member, 'can_manage_labels', 'manage_labels', 'Etiquetas')}
                    ${permCheckbox(member, 'can_delete_cards', 'delete_cards', 'Eliminar tareas')}
                    ${permCheckbox(member, 'can_edit_lists', 'edit_lists', 'Editar listas')}
                    ${permCheckbox(member, 'can_invite', 'invite_members', 'Invitar')}
                </div>
            </div>
        ` : '';

        return `
            <div class="member-mgmt-row p-3 rounded mb-2" data-membership-id="${member.membership_id}">
                <div class="d-flex justify-content-between align-items-start flex-wrap gap-2">
                    <div>
                        <strong>${FlowTaskHelpers.escapeHtml(member.username)}</strong>
                        <span class="badge bg-light text-dark ms-1">${member.role_display}</span>
                        <small class="text-muted d-block">Desde ${member.joined_at}</small>
                    </div>
                    ${canManage ? `
                    <div class="d-flex gap-2 align-items-start">
                        <select class="form-select form-select-sm member-role-select" style="width:auto;">
                            <option value="member" ${member.role === 'member' ? 'selected' : ''}>Miembro</option>
                            <option value="viewer" ${member.role === 'viewer' ? 'selected' : ''}>Espectador</option>
                            <option value="admin" ${member.role === 'admin' ? 'selected' : ''}>Administrador</option>
                        </select>
                        <button class="btn btn-sm btn-primary save-permissions-btn" data-id="${member.membership_id}">
                            <i class="fas fa-save"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger remove-member-btn" data-id="${member.membership_id}" data-name="${FlowTaskHelpers.escapeHtml(member.username)}">
                            <i class="fas fa-user-minus"></i>
                        </button>
                    </div>
                    ` : ''}
                </div>
                ${canManage ? permsHtml : ''}
            </div>
        `;
    }

    function permCheckbox(member, field, permKey, label) {
        const isChecked = member.permissions?.[permKey] || false;
        return `
            <label class="form-check-label small">
                <input type="checkbox" class="form-check-input perm-check" name="${field}" ${isChecked ? 'checked' : ''}>
                ${label}
            </label>
        `;
    }

    async function savePermissions(btn) {
        const row = btn.closest('.member-mgmt-row');
        const membershipId = row.dataset.membershipId;
        const role = row.querySelector('.member-role-select')?.value;
        const formData = new FormData();
        formData.append('role', role);
        row.querySelectorAll('.perm-check').forEach(cb => {
            if (cb.checked) formData.append(cb.name, 'on');
        });

        btn.disabled = true;
        try {
            const response = await fetch(`/boards/members/${membershipId}/permissions/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': FlowTaskHelpers.getCSRFToken(),
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: formData,
                credentials: 'same-origin',
            });
            const data = await response.json();
            if (data.success) {
                FlowTaskHelpers.showToast('Permisos actualizados', 'success');
            } else {
                FlowTaskHelpers.showToast(data.error || 'Error', 'error');
            }
        } catch (error) {
            FlowTaskHelpers.showToast('Error al guardar', 'error');
        } finally {
            btn.disabled = false;
        }
    }

    async function removeMember(btn) {
        const name = btn.dataset.name;
        const membershipId = btn.dataset.id;
        if (!confirm(`¿Remover a ${name} del tablero?`)) return;

        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/boards/members/${membershipId}/remove/`;
        const csrf = document.createElement('input');
        csrf.type = 'hidden';
        csrf.name = 'csrfmiddlewaretoken';
        csrf.value = FlowTaskHelpers.getCSRFToken();
        form.appendChild(csrf);
        document.body.appendChild(form);
        form.submit();
    }
})();
