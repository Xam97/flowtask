<<<<<<< HEAD
// static/js/dashboard.js
// Funcionalidades del dashboard y gestión de tableros

=======
>>>>>>> origin/camilarodas
(function() {
    'use strict';
    
    // Esperar a que DOM esté listo
    document.addEventListener('DOMContentLoaded', () => {
        initDashboard();
        initSidebar();
        initCreateBoardModal();
    });
    
<<<<<<< HEAD
    /**
     * Inicializa el dashboard
     */
    function initDashboard() {
        console.log('Dashboard inicializado');
        
        // Cargar tableros recientes en sidebar
        loadRecentBoards();
        
        // Configurar eventos de las tarjetas de tablero
        setupBoardCards();
    }
    
    /**
     * Inicializa la sidebar responsive
     */
=======
    function initDashboard() {
        console.log('Dashboard inicializado');
        setupBoardCards();
    }
    
>>>>>>> origin/camilarodas
    function initSidebar() {
        const sidebar = document.getElementById('sidebar');
        const toggleBtn = document.getElementById('sidebarToggle');
        
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => {
                sidebar.classList.toggle('collapsed');
<<<<<<< HEAD
                
                // Guardar preferencia en localStorage
=======
>>>>>>> origin/camilarodas
                const isCollapsed = sidebar.classList.contains('collapsed');
                localStorage.setItem('sidebarCollapsed', isCollapsed);
            });
        }
        
<<<<<<< HEAD
        // Restaurar estado colapsado
        const savedState = localStorage.getItem('sidebarCollapsed');
        if (savedState === 'true') {
            sidebar.classList.add('collapsed');
        }
        
        // Para mobile: cerrar sidebar al hacer click fuera
        if (window.innerWidth <= 768) {
            document.addEventListener('click', (e) => {
                if (!sidebar.contains(e.target) && !e.target.closest('.navbar-toggler')) {
                    sidebar.classList.remove('mobile-open');
                }
=======
        const savedState = localStorage.getItem('sidebarCollapsed');
        if (savedState === 'true' && sidebar) {
            sidebar.classList.add('collapsed');
        }
        
        // Mobile sidebar
        const navbarToggler = document.querySelector('.navbar-toggler');
        if (navbarToggler && sidebar) {
            navbarToggler.addEventListener('click', () => {
                sidebar.classList.toggle('mobile-open');
>>>>>>> origin/camilarodas
            });
        }
    }
    
<<<<<<< HEAD
    /**
     * Carga los tableros recientes en la sidebar
     */
    function loadRecentBoards() {
        // TODO: Implementar carga real desde API
        const recentBoards = JSON.parse(localStorage.getItem('recentBoards') || '[]');
        const boardList = document.querySelector('.board-list');
        
        if (boardList && recentBoards.length > 0) {
            boardList.innerHTML = recentBoards.map(board => `
                <div class="board-item" data-board-id="${board.id}">
                    <i class="fas fa-columns"></i>
                    <span>${escapeHtml(board.name)}</span>
                </div>
            `).join('');
        }
    }
    
    /**
     * Guarda un tablero como reciente
     */
    function saveRecentBoard(board) {
        let recentBoards = JSON.parse(localStorage.getItem('recentBoards') || '[]');
        
        // Remover si ya existe
        recentBoards = recentBoards.filter(b => b.id !== board.id);
        
        // Agregar al principio
        recentBoards.unshift({ id: board.id, name: board.name });
        
        // Limitar a 5 recientes
        recentBoards = recentBoards.slice(0, 5);
        
        localStorage.setItem('recentBoards', JSON.stringify(recentBoards));
        loadRecentBoards();
    }
    
    /**
     * Configura eventos de las tarjetas de tablero
     */
    function setupBoardCards() {
        const boardCards = document.querySelectorAll('.board-card');
        
        boardCards.forEach(card => {
            card.addEventListener('click', (e) => {
                // Evitar si se hizo click en un botón
                if (e.target.closest('.btn') || e.target.closest('button')) {
                    return;
                }
                
                const boardId = card.dataset.boardId;
                if (boardId) {
                    openBoard(boardId);
=======
    function setupBoardCards() {
        const boardCards = document.querySelectorAll('.board-card');
        boardCards.forEach(card => {
            card.addEventListener('click', (e) => {
                if (e.target.closest('.btn') || e.target.closest('button')) {
                    return;
                }
                const boardLink = card.querySelector('a[href*="/boards/"]');
                if (boardLink) {
                    window.location.href = boardLink.getAttribute('href');
>>>>>>> origin/camilarodas
                }
            });
        });
    }
    
<<<<<<< HEAD
    /**
     * Abre un tablero
     */
    function openBoard(boardId) {
        // TODO: Implementar navegación a vista de tablero
        console.log(`Abriendo tablero ${boardId}`);
        // window.location.href = `/boards/${boardId}/`;
    }
    
    /**
     * Inicializa el modal de crear tablero
     */
    function initCreateBoardModal() {
        const saveBtn = document.getElementById('saveBoardBtn');
        
        if (saveBtn) {
            saveBtn.addEventListener('click', createBoard);
        }
    }
    
    /**
     * Crea un nuevo tablero vía API
     */
    async function createBoard() {
        const nameInput = document.getElementById('boardName');
        const descInput = document.getElementById('boardDescription');
        
        const name = nameInput?.value.trim();
        const description = descInput?.value.trim();
        
        if (!name) {
            FlowTaskHelpers.showToast('El nombre del tablero es requerido', 'error');
            return;
        }
        
        if (name.length < 3) {
            FlowTaskHelpers.showToast('El nombre debe tener al menos 3 caracteres', 'error');
            return;
        }
        
        try {
            const data = await FlowTaskHelpers.apiFetch('/boards/api/create/', {
                method: 'POST',
                body: JSON.stringify({ name, description })
            });
            
            if (data.success) {
                FlowTaskHelpers.showToast('Tablero creado exitosamente', 'success');
                
                // Cerrar modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('createBoardModal'));
                modal.hide();
                
                // Limpiar formulario
                nameInput.value = '';
                descInput.value = '';
                
                // Recargar página o agregar tarjeta dinámicamente
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                FlowTaskHelpers.showToast(data.error || 'Error al crear tablero', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            FlowTaskHelpers.showToast('Error al crear tablero', 'error');
        }
    }
    
    /**
     * Escapa HTML para prevenir XSS
     */
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
=======
    function initCreateBoardModal() {
        // El formulario ya envía con POST normal, no necesita JavaScript adicional
        console.log('Modal de creación de tablero listo');
>>>>>>> origin/camilarodas
    }
})();