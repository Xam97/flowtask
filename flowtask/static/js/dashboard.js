// Dashboard, sidebar, recent boards, create board modal
(function() {
    'use strict';

    window.saveRecentBoard = saveRecentBoard;

    document.addEventListener('DOMContentLoaded', () => {
        initSidebar();
        initCreateBoardModal();
        loadRecentBoards();
        setupBoardCards();
        trackCurrentBoard();
        setupRecentBoardClicks();
        initLiveMembershipUpdates();
    });

    function initSidebar() {
        const sidebar = document.getElementById('sidebar');
        const toggleBtn = document.getElementById('sidebarToggle');
        const mobileToggle = document.getElementById('mobileSidebarToggle');

        if (toggleBtn && sidebar) {
            toggleBtn.addEventListener('click', () => {
                sidebar.classList.toggle('collapsed');
                localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
            });
        }

        if (localStorage.getItem('sidebarCollapsed') === 'true' && sidebar) {
            sidebar.classList.add('collapsed');
        }

        if (mobileToggle && sidebar) {
            mobileToggle.addEventListener('click', (e) => {
                e.stopPropagation();
                sidebar.classList.toggle('mobile-open');
            });

            document.addEventListener('click', (e) => {
                if (window.innerWidth <= 768) {
                    if (!sidebar.contains(e.target) && !mobileToggle.contains(e.target)) {
                        sidebar.classList.remove('mobile-open');
                    }
                }
            });
        }
    }

    async function loadRecentBoards() {
        const recentBoards = JSON.parse(localStorage.getItem('recentBoards') || '[]');
        const boardList = document.getElementById('recentBoardsList');
        if (!boardList) return;

        if (recentBoards.length === 0) {
            boardList.innerHTML = `
                <div class="board-item board-item-empty" style="opacity:0.5;font-size:0.7rem;padding:0.375rem 0.5rem;">
                    <span>Sin tableros recientes</span>
                </div>
            `;
            return;
        }

        // Fetch user's owned boards to filter recent boards
        try {
            const response = await fetch('/boards/api/user-owned-boards/', { credentials: 'same-origin' });
            const data = await response.json();
            const ownedBoardIds = new Set(data.owned_board_ids || []);
            
            const filteredBoards = recentBoards.filter(board => ownedBoardIds.has(board.id));
            
            if (filteredBoards.length === 0) {
                boardList.innerHTML = `
                    <div class="board-item board-item-empty" style="opacity:0.5;font-size:0.7rem;padding:0.375rem 0.5rem;">
                        <span>Sin tableros recientes</span>
                    </div>
                `;
                return;
            }

            boardList.innerHTML = filteredBoards.map(board => `
                <a href="/boards/${board.id}/" class="board-item" data-board-id="${board.id}">
                    <i class="fas fa-columns"></i>
                    <span>${FlowTaskHelpers.escapeHtml(board.name)}</span>
                </a>
            `).join('');
        } catch (error) {
            console.error('Error loading recent boards:', error);
            boardList.innerHTML = `
                <div class="board-item board-item-empty" style="opacity:0.5;font-size:0.7rem;padding:0.375rem 0.5rem;">
                    <span>Error al cargar recientes</span>
                </div>
            `;
        }
    }

    function saveRecentBoard(board) {
        let recentBoards = JSON.parse(localStorage.getItem('recentBoards') || '[]');
        recentBoards = recentBoards.filter(b => b.id !== board.id);
        recentBoards.unshift({ id: board.id, name: board.name });
        recentBoards = recentBoards.slice(0, 5);
        localStorage.setItem('recentBoards', JSON.stringify(recentBoards));
        loadRecentBoards();
    }

    function trackCurrentBoard() {
        const boardEl = document.querySelector('[data-board-id][data-board-name]');
        if (boardEl) {
            saveRecentBoard({
                id: parseInt(boardEl.dataset.boardId),
                name: boardEl.dataset.boardName,
            });
        }
    }

    function setupRecentBoardClicks() {
        document.addEventListener('click', (e) => {
            const item = e.target.closest('.board-item[data-board-id]');
            if (item) {
                const name = item.querySelector('span')?.textContent;
                saveRecentBoard({ id: parseInt(item.dataset.boardId), name });
            }
        });
    }

    function setupBoardCards() {
        document.querySelectorAll('.board-card').forEach(card => {
            card.addEventListener('click', (e) => {
                if (e.target.closest('.btn') || e.target.closest('a')) return;
                const link = card.querySelector('.board-open-link');
                if (link) {
                    const boardId = card.dataset.boardId;
                    const boardName = card.dataset.boardName;
                    if (boardId && boardName) saveRecentBoard({ id: parseInt(boardId), name: boardName });
                    window.location.href = link.href;
                }
            });
        });
    }

    function initCreateBoardModal() {
        const saveBtn = document.getElementById('saveBoardBtn');
        if (saveBtn) saveBtn.addEventListener('click', createBoard);
    }

    async function createBoard() {
        const nameInput = document.getElementById('boardName');
        const descInput = document.getElementById('boardDescription');
        const name = nameInput?.value.trim();
        const description = descInput?.value.trim() || '';

        if (!name || name.length < 3) {
            FlowTaskHelpers.showToast('El nombre debe tener al menos 3 caracteres', 'error');
            return;
        }

        const formData = new FormData();
        formData.append('name', name);
        formData.append('description', description);
        formData.append('csrfmiddlewaretoken', FlowTaskHelpers.getCSRFToken());

        try {
            const response = await fetch('/boards/create/', {
                method: 'POST',
                body: formData,
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                credentials: 'same-origin',
            });
            const data = await response.json();

            if (data.success) {
                FlowTaskHelpers.showToast('Tablero creado exitosamente', 'success');
                const modalEl = document.getElementById('createBoardModal');
                if (modalEl) bootstrap.Modal.getInstance(modalEl)?.hide();
                if (nameInput) nameInput.value = '';
                if (descInput) descInput.value = '';
                setTimeout(() => { window.location.href = data.board.url; }, 600);
            } else {
                FlowTaskHelpers.showToast(data.error || 'Error al crear tablero', 'error');
            }
        } catch (error) {
            FlowTaskHelpers.showToast('Error al crear tablero', 'error');
        }
    }
    // ================= ACTUALIZACIÓN EN VIVO AL SER AGREGADO A UN TABLERO =================

    function initLiveMembershipUpdates() {
        const dashboard = document.querySelector('.dashboard-container');
        if (!dashboard || !window.FlowTaskWebSocket) return;

        FlowTaskWebSocket.on('onNotification', (data) => {
            if (data.type === 'member_added' && data.board_id) {
                handleAddedToBoard(data.board_id);
            }
        });
    }

    async function handleAddedToBoard(boardId) {
        // Evitamos duplicar la card si por algún motivo ya está en el DOM
        if (document.querySelector(`.board-card[data-board-id="${boardId}"]`)) return;

        try {
            const response = await fetch(`/boards/api/board-summary/${boardId}/`, { credentials: 'same-origin' });
            const data = await response.json();
            if (!data.success) return;

            insertCollaborationBoardCard(data.board);
            setupBoardCards(); // re-engancha el click handler para la card nueva
            FlowTaskHelpers.showToast(`Te agregaron al tablero "${data.board.name}"`, 'success');
        } catch (error) {
            console.error('Error cargando resumen del tablero nuevo:', error);
        }
    }

    function insertCollaborationBoardCard(board) {
        let grid = document.getElementById('collaborationsGrid');
        let badge = document.getElementById('collaborationsCountBadge');

        if (!grid) {
            const section = document.createElement('div');
            section.className = 'boards-section';
            section.id = 'collaborationsSection';
            section.innerHTML = `
                <div class="section-header">
                    <h2><i class="fas fa-users me-1"></i> Colaboraciones</h2>
                    <span class="count-badge" id="collaborationsCountBadge">0</span>
                </div>
                <div class="boards-grid" id="collaborationsGrid"></div>
            `;
            document.querySelector('.dashboard-container').appendChild(section);
            grid = document.getElementById('collaborationsGrid');
            badge = document.getElementById('collaborationsCountBadge');
        }

        const hueBase = 300 + ((board.id * 17) % 60);
        const cardHTML = `
            <div class="board-card" data-board-id="${board.id}" data-board-name="${FlowTaskHelpers.escapeHtml(board.name)}">
                <div class="board-card-header">
                    <div class="board-gradient" style="background: linear-gradient(135deg, hsl(${hueBase},65%,55%) 0%, hsl(${hueBase + 30},55%,45%) 100%);"></div>
                    <span class="board-icon"><i class="fas fa-users"></i></span>
                </div>
                <div class="board-card-body">
                    <h3>${FlowTaskHelpers.escapeHtml(board.name)}</h3>
                    <p>${FlowTaskHelpers.escapeHtml(board.description || 'Sin descripción')}</p>
                    <div class="board-stats">
                        <span><i class="fas fa-list"></i> ${board.lists_count} listas</span>
                        <span><i class="fas fa-tasks"></i> ${board.cards_count} tareas</span>
                    </div>
                </div>
                <div class="board-card-footer">
                    <a href="/boards/${board.id}/" class="btn btn-sm btn-outline-primary board-open-link">Abrir</a>
                </div>
            </div>
        `;

        grid.insertAdjacentHTML('afterbegin', cardHTML);
        if (badge) badge.textContent = grid.querySelectorAll('.board-card').length;
    }
})();
