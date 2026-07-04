// API y utilidades para etiquetas dinámicas

window.FlowTaskLabels = (function() {
    'use strict';

    async function toggleCardLabel(cardId, labelId) {
        try {
            const response = await fetch(`/boards/cards/${cardId}/labels/${labelId}/toggle/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': FlowTaskHelpers.getCSRFToken(),
                    'X-Requested-With': 'XMLHttpRequest',
                },
                credentials: 'same-origin',
            });
            return await response.json();
        } catch (error) {
            console.error('Error toggling label:', error);
            return { success: false, error: 'Error de conexión' };
        }
    }

    async function fetchLabels(boardId) {
        const url = boardId ? `/boards/labels/api/?board_id=${boardId}` : '/boards/labels/api/';
        const response = await fetch(url, { credentials: 'same-origin' });
        return response.json();
    }

    async function createLabel(boardId, name, color) {
        const response = await fetch('/boards/labels/create/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': FlowTaskHelpers.getCSRFToken(),
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: JSON.stringify({ board_id: boardId, name, color }),
            credentials: 'same-origin',
        });
        return response.json();
    }

    async function updateLabel(labelId, name, color) {
        const response = await fetch(`/boards/labels/${labelId}/update/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': FlowTaskHelpers.getCSRFToken(),
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: JSON.stringify({ name, color }),
            credentials: 'same-origin',
        });
        return response.json();
    }

    async function deleteLabel(labelId) {
        const response = await fetch(`/boards/labels/${labelId}/delete/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': FlowTaskHelpers.getCSRFToken(),
                'X-Requested-With': 'XMLHttpRequest',
            },
            credentials: 'same-origin',
        });
        return response.json();
    }

    function renderLabelCard(label, canManage) {
        return `
            <div class="label-card" data-label-id="${label.id}">
                <div class="label-header">
                    <div class="label-color" style="background:${label.color};"></div>
                    <div>
                        <div class="label-name">${FlowTaskHelpers.escapeHtml(label.name)}</div>
                        <div class="label-board">${FlowTaskHelpers.escapeHtml(label.board_name)}</div>
                    </div>
                </div>
                <div class="label-meta">
                    <span><i class="fas fa-tasks"></i> ${label.card_count} tarea${label.card_count !== 1 ? 's' : ''}</span>
                    ${canManage ? `
                    <div class="label-actions">
                        <button class="btn btn-sm btn-icon text-primary edit-label-btn" title="Editar"
                                data-id="${label.id}" data-name="${FlowTaskHelpers.escapeHtml(label.name)}" data-color="${label.color}">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-icon text-danger delete-label-btn" title="Eliminar" data-id="${label.id}">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    return {
        toggleCardLabel,
        fetchLabels,
        createLabel,
        updateLabel,
        deleteLabel,
        renderLabelCard,
    };
})();

// Página de gestión de etiquetas
document.addEventListener('DOMContentLoaded', () => {
    const labelsGrid = document.getElementById('labelsGrid');
    if (!labelsGrid) return;

    initColorPickers(document);
    initLabelsPage(labelsGrid);
});

function initColorPickers(container) {
    container.querySelectorAll('.color-option').forEach(el => {
        el.addEventListener('click', () => {
            const picker = el.closest('.color-picker');
            picker?.querySelectorAll('.color-option').forEach(o => o.classList.remove('selected'));
            el.classList.add('selected');
            el.querySelector('input').checked = true;
        });
    });
    container.querySelector('.color-option')?.classList.add('selected');
}

function initLabelsPage(grid) {
    const createForm = document.getElementById('createLabelForm');
    const editForm = document.getElementById('editLabelForm');
    const boardFilter = document.getElementById('boardFilter');

    boardFilter?.addEventListener('change', () => refreshLabels(grid, boardFilter.value));

    createForm?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const boardId = createForm.querySelector('[name=board_id]').value;
        const name = createForm.querySelector('[name=name]').value.trim();
        const color = createForm.querySelector('[name=color]:checked')?.value || '#579bfc';

        const result = await FlowTaskLabels.createLabel(boardId, name, color);
        if (result.success) {
            FlowTaskHelpers.showToast('Etiqueta creada', 'success');
            bootstrap.Modal.getInstance(document.getElementById('createLabelModal'))?.hide();
            createForm.reset();
            refreshLabels(grid, boardFilter?.value);
        } else {
            FlowTaskHelpers.showToast(result.error || 'Error', 'error');
        }
    });

    editForm?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const labelId = editForm.dataset.labelId;
        const name = editForm.querySelector('[name=name]').value.trim();
        const color = editForm.querySelector('[name=color]:checked')?.value || '#579bfc';

        const result = await FlowTaskLabels.updateLabel(labelId, name, color);
        if (result.success) {
            FlowTaskHelpers.showToast('Etiqueta actualizada', 'success');
            bootstrap.Modal.getInstance(document.getElementById('editLabelModal'))?.hide();
            refreshLabels(grid, boardFilter?.value);
        } else {
            FlowTaskHelpers.showToast(result.error || 'Error', 'error');
        }
    });

    grid.addEventListener('click', async (e) => {
        const editBtn = e.target.closest('.edit-label-btn');
        const deleteBtn = e.target.closest('.delete-label-btn');

        if (editBtn) openEditModal(editBtn);
        if (deleteBtn) await handleDelete(deleteBtn, grid, boardFilter?.value);
    });
}

async function refreshLabels(grid, boardId) {
    grid.innerHTML = '<div class="text-center py-4" style="grid-column:1/-1;"><i class="fas fa-spinner fa-spin"></i></div>';
    const data = await FlowTaskLabels.fetchLabels(boardId || null);

    if (!data.success || !data.labels.length) {
        grid.innerHTML = `
            <div class="empty-state" style="grid-column:1/-1;">
                <i class="fas fa-tags"></i>
                <p>No hay etiquetas. Crea una para organizar tus tareas.</p>
            </div>`;
        return;
    }

    const perms = window.labelPermissions || {};
    grid.innerHTML = data.labels.map(l => {
        const canManage = perms[String(l.board_id)]?.manage_labels === true;
        return FlowTaskLabels.renderLabelCard(l, canManage);
    }).join('');
}

function openEditModal(btn) {
    const modal = document.getElementById('editLabelModal');
    const form = document.getElementById('editLabelForm');
    if (!modal || !form) return;

    form.dataset.labelId = btn.dataset.id;
    form.querySelector('[name=name]').value = btn.dataset.name;

    form.querySelectorAll('.color-option').forEach(opt => {
        const input = opt.querySelector('input');
        const selected = input.value === btn.dataset.color;
        input.checked = selected;
        opt.classList.toggle('selected', selected);
    });

    new bootstrap.Modal(modal).show();
}

async function handleDelete(btn, grid, boardId) {
    if (!confirm('¿Eliminar esta etiqueta? Se desvinculará de todas las tareas.')) return;
    const result = await FlowTaskLabels.deleteLabel(btn.dataset.id);
    if (result.success) {
        FlowTaskHelpers.showToast('Etiqueta eliminada', 'success');
        refreshLabels(grid, boardId);
    } else {
        FlowTaskHelpers.showToast(result.error || 'Error', 'error');
    }
}
