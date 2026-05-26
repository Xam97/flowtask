(function() {
    'use strict';
    
    // Esperar a que DOM esté listo
    document.addEventListener('DOMContentLoaded', () => {
        initDashboard();
        initSidebar();
        initCreateBoardModal();
    });
    
    function initDashboard() {
        console.log('Dashboard inicializado');
        setupBoardCards();
    }
    
    function initSidebar() {
        const sidebar = document.getElementById('sidebar');
        const toggleBtn = document.getElementById('sidebarToggle');
        
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => {
                sidebar.classList.toggle('collapsed');
                const isCollapsed = sidebar.classList.contains('collapsed');
                localStorage.setItem('sidebarCollapsed', isCollapsed);
            });
        }
        
        const savedState = localStorage.getItem('sidebarCollapsed');
        if (savedState === 'true' && sidebar) {
            sidebar.classList.add('collapsed');
        }
        
        // Mobile sidebar
        const navbarToggler = document.querySelector('.navbar-toggler');
        if (navbarToggler && sidebar) {
            navbarToggler.addEventListener('click', () => {
                sidebar.classList.toggle('mobile-open');
            });
        }
    }
    
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
                }
            });
        });
    }
    
    function initCreateBoardModal() {
        // El formulario ya envía con POST normal, no necesita JavaScript adicional
        console.log('Modal de creación de tablero listo');
    }
})();