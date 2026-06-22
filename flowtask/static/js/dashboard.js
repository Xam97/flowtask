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

    function loadRecentBoards() {
        const recentBoards = JSON.parse(localStorage.getItem('recentBoards') || '[]');
        const boardList = document.getElementById('recentBoardsList');
        if (!boardList) return;

        if (recentBoards.length === 0) return;

        boardList.innerHTML = recentBoards.map(board => `
            <a href="/boards/${board.id}/" class="board-item" data-board-id="${board.id}">
                <i class="fas fa-columns"></i>
                <span>${FlowTaskHelpers.escapeHtml(board.name)}</span>
            </a>
        `).join('');
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
})();
