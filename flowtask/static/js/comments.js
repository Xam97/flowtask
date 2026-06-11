// Modal de tarea con comentarios en tiempo real

(function() {
    'use strict';

    let currentCardId = null;
    let cardModal = null;

    document.addEventListener('DOMContentLoaded', () => {
        const boardContainer = document.querySelector('.kanban-container');
        if (!boardContainer) return;

        const modalEl = document.getElementById('cardDetailModal');
        if (modalEl) {
            cardModal = new bootstrap.Modal(modalEl);
        }

        initCardClicks();
        initCommentForm();
        initWebSocketHandlers();

        const boardId = boardContainer.dataset.boardId;
        if (boardId) {
            FlowTaskWebSocket.connectToBoard(boardId);
        }
    });

    function initCardClicks() {
        document.querySelectorAll('.card-item').forEach(card => {
            card.addEventListener('click', (e) => {
                if (e.target.closest('a, button, form')) return;
                openCardModal(card.dataset.cardId);
            });
        });
    }

    async function openCardModal(cardId) {
        currentCardId = cardId;
        const body = document.getElementById('cardModalBody');
        const title = document.getElementById('cardModalTitle');
        if (!body) return;

        body.innerHTML = '<div class="text-center py-4"><div class="spinner-border text-primary"></div></div>';
        cardModal?.show();

        try {
            const response = await fetch(`/comments/card/${cardId}/`, { credentials: 'same-origin' });
            const data = await response.json();

            if (!data.success) {
                body.innerHTML = `<div class="alert alert-warning">${FlowTaskHelpers.escapeHtml(data.error)}</div>`;
                document.getElementById('cardCommentForm')?.classList.add('d-none');
                return;
            }

            title.textContent = data.card.title;
            renderCardDetail(data.card, data.comments, data.can_comment);
            const form = document.getElementById('cardCommentForm');
            if (data.can_comment) {
                form?.classList.remove('d-none');
            } else {
                form?.classList.add('d-none');
            }
        } catch (error) {
            body.innerHTML = '<div class="alert alert-danger">Error al cargar la tarea</div>';
        }
    }

    function renderCardDetail(card, comments, canComment) {
        const body = document.getElementById('cardModalBody');
        const priorityLabels = { low: 'Baja', medium: 'Media', high: 'Alta', urgent: 'Urgente' };

        body.innerHTML = `
            <div class="card-detail-meta">
                <div class="meta-item">
                    <i class="fas fa-list"></i>
                    <span>${FlowTaskHelpers.escapeHtml(card.list_name)}</span>
                </div>
                <div class="meta-item">
                    <i class="fas fa-flag"></i>
                    <span class="priority-label priority-${card.priority}">${priorityLabels[card.priority] || card.priority}</span>
                </div>
                <div class="meta-item">
                    <i class="fas fa-user-check"></i>
                    <span>${FlowTaskHelpers.escapeHtml(card.assigned_to || 'Sin asignar')}</span>
                </div>
                <div class="meta-item">
                    <i class="fas fa-user-edit"></i>
                    <span>Creada por ${FlowTaskHelpers.escapeHtml(card.created_by)}</span>
                </div>
            </div>
            ${card.description ? `<div class="card-detail-description">${FlowTaskHelpers.escapeHtml(card.description)}</div>` : ''}
            <div class="comments-section">
                <h6><i class="fas fa-comments me-2"></i>Comentarios <span class="comment-count-badge">${comments.length}</span></h6>
                ${canComment ? '' : '<p class="text-muted small"><i class="fas fa-info-circle"></i> Asigna esta tarea a alguien para habilitar comentarios.</p>'}
                <div class="comments-container" data-card-id="${card.id}">
                    ${comments.map(c => renderCommentHtml(c)).join('') || (canComment ? '<p class="text-muted small">Sin comentarios aún. ¡Sé el primero!</p>' : '')}
                </div>
            </div>
        `;

        bindDeleteButtons();
    }

    function renderCommentHtml(comment) {
        const currentUserId = document.body.dataset.userId;
        const canDelete = comment.is_own || comment.user_id == currentUserId;
        return `
            <div class="comment-item" data-comment-id="${comment.id || comment.comment_id}">
                <div class="comment-header">
                    <div class="comment-avatar">${comment.user.charAt(0).toUpperCase()}</div>
                    <div>
                        <strong>${FlowTaskHelpers.escapeHtml(comment.user)}</strong>
                        <small>${comment.created_at}</small>
                    </div>
                    ${canDelete ? `<button class="btn btn-sm btn-link text-danger delete-comment-btn" data-id="${comment.id || comment.comment_id}"><i class="fas fa-trash-alt"></i></button>` : ''}
                </div>
                <p>${FlowTaskHelpers.escapeHtml(comment.content || comment.comment)}</p>
            </div>
        `;
    }

    function bindDeleteButtons() {
        document.querySelectorAll('.delete-comment-btn').forEach(btn => {
            btn.addEventListener('click', async () => {
                if (!confirm('¿Eliminar este comentario?')) return;
                try {
                    const response = await fetch(`/comments/delete/${btn.dataset.id}/`, {
                        method: 'POST',
                        headers: { 'X-CSRFToken': FlowTaskHelpers.getCSRFToken() },
                        credentials: 'same-origin',
                    });
                    const data = await response.json();
                    if (data.success) {
                        btn.closest('.comment-item')?.remove();
                        updateCommentCount(-1);
                        updateCardCommentBadge(currentCardId, -1);
                    }
                } catch (error) {
                    FlowTaskHelpers.showToast('Error al eliminar', 'error');
                }
            });
        });
    }

    function initCommentForm() {
        const form = document.getElementById('cardCommentForm');
        if (!form) return;

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            if (!currentCardId) return;

            const input = form.querySelector('textarea');
            const content = input.value.trim();
            if (!content) return;

            const submitBtn = form.querySelector('button[type="submit"]');
            submitBtn.disabled = true;

            try {
                const formData = new FormData();
                formData.append('content', content);

                const response = await fetch(`/comments/add/${currentCardId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': FlowTaskHelpers.getCSRFToken(),
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                    credentials: 'same-origin',
                    body: formData,
                });
                const data = await response.json();

                if (data.success) {
                    input.value = '';
                    appendComment(data.comment);
                    updateCommentCount(1);
                    updateCardCommentBadge(currentCardId, 1);
                } else {
                    FlowTaskHelpers.showToast(data.error || 'Error', 'error');
                }
            } catch (error) {
                FlowTaskHelpers.showToast('Error al comentar', 'error');
            } finally {
                submitBtn.disabled = false;
            }
        });
    }

    function appendComment(comment) {
        const container = document.querySelector(`.comments-container[data-card-id="${currentCardId}"]`);
        if (container) {
            container.insertAdjacentHTML('beforeend', renderCommentHtml(comment));
            bindDeleteButtons();
        }
    }

    function updateCommentCount(delta) {
        const badge = document.querySelector('.comment-count-badge');
        if (badge) {
            badge.textContent = Math.max(0, (parseInt(badge.textContent) || 0) + delta);
        }
    }

    function updateCardCommentBadge(cardId, delta) {
        const card = document.querySelector(`.card-item[data-card-id="${cardId}"]`);
        if (!card) return;
        let badge = card.querySelector('.comment-badge');
        const current = badge ? parseInt(badge.textContent) + delta : delta;
        if (current > 0) {
            if (!badge) {
                card.querySelector('.card-meta')?.insertAdjacentHTML('beforeend',
                    `<span class="comment-badge"><i class="fas fa-comment"></i> ${current}</span>`
                );
            } else {
                badge.innerHTML = `<i class="fas fa-comment"></i> ${current}`;
            }
        } else if (badge) {
            badge.remove();
        }
    }

    function initWebSocketHandlers() {
        FlowTaskWebSocket.on('onNewComment', (data) => {
            if (data.card_id == currentCardId) {
                const container = document.querySelector(`.comments-container[data-card-id="${data.card_id}"]`);
                const existing = container?.querySelector(`[data-comment-id="${data.comment_id}"]`);
                if (container && !existing) {
                    container.insertAdjacentHTML('beforeend', renderCommentHtml(data));
                    bindDeleteButtons();
                    updateCommentCount(1);
                }
            }
            updateCardCommentBadge(data.card_id, 1);
        });
    }
})();
