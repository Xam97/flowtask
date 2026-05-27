// static/js/dashboard.js
// Funcionalidades del dashboard y gestión de tableros

(function() {
    'use strict';
    
    // Esperar a que DOM esté listo
    document.addEventListener('DOMContentLoaded', () => {
        initDashboard();
        initSidebar();
        initCreateBoardModal();
    });
    
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
     * Inicializa la sidebar responsive y guarda preferencias del usuario
     */
    function initSidebar() {
        const sidebar = document.getElementById('sidebar');
        const toggleBtn = document.getElementById('sidebarToggle');
        
        if (toggleBtn && sidebar) {
            toggleBtn.addEventListener('click', () => {
                sidebar.classList.toggle('collapsed');
                
                // Guardar preferencia en localStorage
                const isCollapsed = sidebar.classList.contains('collapsed');
                localStorage.setItem('sidebarCollapsed', isCollapsed);
            });
        }
        
        // Restaurar estado colapsado anterior
        const savedState = localStorage.getItem('sidebarCollapsed');
        if (savedState === 'true' && sidebar) {
            sidebar.classList.add('collapsed');
        }
        
        // Comportamiento Mobile para la sidebar
        const navbarToggler = document.querySelector('.navbar-toggler');
        if (navbarToggler && sidebar) {
            navbarToggler.addEventListener('click', () => {
                sidebar.classList.toggle('mobile-open');
            });
            
            // Cerrar sidebar al hacer click fuera en dispositivos móviles
            document.addEventListener('click', (e) => {
                if (window.innerWidth <= 768) {
                    if (!sidebar.contains(e.target) && !e.target.closest('.navbar-toggler')) {
                        sidebar.classList.remove('mobile-open');
                    }
                }
            });
        }
    }
    
    /**
     * Carga los tableros recientes guardados en el almacenamiento local
     */
    function loadRecentBoards() {
        const recentBoards = JSON.parse(localStorage.getItem('recentBoards') || '[]');
        const boardList = document.querySelector('.board-list');
        
        if (boardList && recentBoards.length > 0) {
            boardList.innerHTML = recentBoards.map(board => `
                <div class="board-item" data-board-id="${board.id}">
                    <i class="fas fa-columns"></i>
                    <span>${FlowTaskHelpers.escapeHtml(board.name)}</span>
                </div>
            `).join('');
        }
    }
    
    /**
     * Guarda un tablero abierto como reciente
     */
    function saveRecentBoard(board) {
        let recentBoards = JSON.parse(localStorage.getItem('recentBoards') || '[]');
        
        // Remover si ya existe en la lista
        recentBoards = recentBoards.filter(b => b.id !== board.id);
        
        // Agregar al principio
        recentBoards.unshift({ id: board.id, name: board.name });
        
        // Limitar la lista a los últimos 5 tableros abiertos
        recentBoards = recentBoards.slice(0, 5);
        
        localStorage.setItem('recentBoards', JSON.stringify(recentBoards));
        loadRecentBoards();
    }
    
    /**
     * Configura los disparadores de clicks en los contenedores de tarjetas de tablero
     */
    function setupBoardCards() {
        const boardCards = document.querySelectorAll('.board-card');
        
        boardCards.forEach(card => {
            card.addEventListener('click', (e) => {
                // Evitar redirección si se hizo click en botones internos de edición/eliminación
                if (e.target.closest('.btn') || e.target.closest('button')) {
                    return;
                }
                
                // Intenta navegar usando el enlace interno o el dataset asignado
                const boardLink = card.querySelector('a[href*="/boards/"]');
                if (boardLink) {
                    window.location.href = boardLink.getAttribute('href');
                } else {
                    const boardId = card.dataset.boardId;
                    if (boardId) {
                        openBoard(boardId);
                    }
                }
            });
        });
    }
    
    /**
     * Redirección manual a un tablero por ID
     */
    function openBoard(boardId) {
        console.log(`Abriendo tablero ${boardId}`);
        window.location.href = `/boards/${boardId}/`;
    }
    
    /**
     * Inicializa el modal de crear tablero de forma asíncrona
     */
    function initCreateBoardModal() {
        const saveBtn = document.getElementById('saveBoardBtn');
        if (saveBtn) {
            saveBtn.addEventListener('click', createBoard);
        }
        console.log('Modal de creación de tablero listo');
    }
    
    /**
     * Crea un nuevo tablero comunicándose con la API REST
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
                
                // Cerrar modal de Bootstrap de forma segura
                const modalElement = document.getElementById('createBoardModal');
                if (modalElement) {
                    const modal = bootstrap.Modal.getInstance(modalElement) || new bootstrap.Modal(modalElement);
                    modal.hide();
                }
                
                // Limpiar inputs del formulario
                if (nameInput) nameInput.value = '';
                if (descInput) descInput.value = '';
                
                // Recargar el Dashboard para visualizar los cambios actualizados
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
})();