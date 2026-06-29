// Funcionalidades interactivas de la vista del tablero

(function() {
    'use strict';
    
    let sortableInstances = [];
    let currentBoardId = null;
    
    document.addEventListener('DOMContentLoaded', () => {
        initBoard();
    });
    
    function initBoard() {
        const boardContainer = document.querySelector('.kanban-container');
        if (!boardContainer) return;
        
        currentBoardId = boardContainer.dataset.boardId;
        console.log('Inicializando tablero:', currentBoardId);
        
        initSortable();
        initListActions();
        initCardActions();
    }
    
    /**
     * Inicializar SortableJS para drag & drop
     */
    function initSortable() {
        const boardContainer = document.querySelector('.kanban-container');
        const canMove = boardContainer?.dataset.canMove !== 'false';
        const canReorderLists = boardContainer?.dataset.canReorderLists === 'true';

        document.querySelectorAll('.cards-container').forEach(container => {
            const sortable = new Sortable(container, {
                group: 'cards',
                animation: 200,
                ghostClass: 'sortable-ghost',
                dragClass: 'sortable-drag',
                disabled: !canMove,
                onEnd: async function(evt) {
                    const cardId = evt.item.dataset.cardId;
                    const newListId = evt.to.dataset.listId;
                    const newPosition = evt.newIndex;
                    
                    if (cardId && newListId) {
                        // Mostrar loader
                        FlowTaskHelpers.showToast('Moviendo tarea...', 'info');
                        
                        try {
                            await FlowTaskAPI.updateCardPosition(cardId, newListId, newPosition);
                            FlowTaskHelpers.showToast('Tarea movida', 'success');
                        } catch (error) {
                            console.error('Error al mover:', error);
                            FlowTaskHelpers.showToast('Error al mover tarea', 'error');
                            location.reload();
                        }
                    }
                }
            });
            sortableInstances.push(sortable);
        });
        
        // Configurar ordenamiento de listas (si se desea)
        const kanbanContainer = document.querySelector('.kanban-container');
        if (kanbanContainer && canReorderLists) {
            const listSortable = new Sortable(kanbanContainer, {
                animation: 200,
                handle: '.list-header',
                ghostClass: 'sortable-ghost',
                onEnd: async function(evt) {
                    const listId = evt.item.dataset.listId;
                    const newPosition = evt.newIndex;
                    
                    if (listId) {
                        try {
                            await FlowTaskAPI.updateListPosition(listId, newPosition);
                        } catch (error) {
                            console.error('Error al mover lista:', error);
                        }
                    }
                }
            });
            sortableInstances.push(listSortable);
        }
    }
    
    /**
     * Inicializar acciones de listas (editar, eliminar)
     */
    function initListActions() {
        // Botón eliminar lista
        document.querySelectorAll('.delete-list-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.stopPropagation();
                const listId = btn.dataset.listId;
                const listName = btn.dataset.listName;
                
                if (confirm(`¿Eliminar la lista "${listName}"? Se eliminarán todas las tareas.`)) {
                    try {
                        await FlowTaskAPI.deleteList(listId);
                        FlowTaskHelpers.showToast('Lista eliminada', 'success');
                        location.reload();
                    } catch (error) {
                        FlowTaskHelpers.showToast('Error al eliminar', 'error');
                    }
                }
            });
        });
        
        // Editar lista (redirige a página de edición)
        document.querySelectorAll('.edit-list-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const editUrl = btn.dataset.editUrl;
                if (editUrl) {
                    window.location.href = editUrl;
                }
            });
        });
    }
    
    /**
     * Inicializar acciones de tarjetas
     */
    function initCardActions() {
        // Editar tarjeta
        document.querySelectorAll('.edit-card-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const editUrl = btn.dataset.editUrl;
                if (editUrl) {
                    window.location.href = editUrl;
                }
            });
        });
        
        // Eliminar tarjeta
        document.querySelectorAll('.delete-card-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.stopPropagation();
                const cardId = btn.dataset.cardId;
                const cardTitle = btn.dataset.cardTitle;
                
                if (confirm(`¿Eliminar la tarea "${cardTitle}"?`)) {
                    try {
                        await FlowTaskAPI.deleteCard(cardId);
                        FlowTaskHelpers.showToast('Tarea eliminada', 'success');
                        location.reload();
                    } catch (error) {
                        FlowTaskHelpers.showToast('Error al eliminar', 'error');
                    }
                }
            });
        });
    }
})();