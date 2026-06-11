// static/js/dragdrop.js
// Drag & Drop para mover tarjetas entre listas con soporte en tiempo real y envío asíncrono

let boardSocket = null;

document.addEventListener('DOMContentLoaded', function() {
    console.log('Drag & Drop inicializado');
    
    // 1. Inicializar el comportamiento de arrastre físico (Sortable)
    inicializarSortable();
    
    // 2. Conectar al WebSocket del Tablero para escuchar cambios de otros usuarios
    conectarWebSocketTablero();

    // 3. Inicializar el manejo asíncrono (AJAX) de los formularios de creación de tareas
    inicializarFormulariosTarjetas();
});

/**
 * Inicializa o re-vincula SortableJS en todos los contenedores de tarjetas.
 * Se separa en una función para poder llamarla cada vez que se inyecta una tarjeta en vivo.
 */
function inicializarSortable() {
    const containers = document.querySelectorAll('.cards-container');
    
    if (containers.length === 0) {
        console.log('No se encontraron contenedores de tarjetas');
        return;
    }
    
    containers.forEach(container => {
        // Si el contenedor ya tiene una instancia de Sortable activa, la destruimos para evitar duplicados
        if (Sortable.get(container)) {
            Sortable.get(container).destroy();
        }

        new Sortable(container, {
            group: {
                name: 'cards',
                pull: true,
                revertClone: false
            },
            animation: 200,
            ghostClass: 'sortable-ghost',
            dragClass: 'sortable-drag',
            handle: '.card-item',
            onEnd: async function(evt) {
                const cardId = evt.item.dataset.cardId;
                const newListId = evt.to.dataset.listId;
                const newPosition = evt.newIndex;
                
                // Evitar peticiones si se soltó en el mismo lugar exacto sin cambios
                if (evt.from === evt.to && evt.oldIndex === evt.newIndex) return;
                if (!cardId || !newListId) return;
                
                console.log(`Moviendo tarjeta ${cardId} a lista ${newListId} posicion ${newPosition}`);
                
                // Mostrar indicador visual de carga
                evt.item.style.opacity = '0.5';
                
                try {
                    // Obtener CSRF token
                    let csrfToken = obtenerCsrfToken();
                    
                    const response = await fetch('/boards/cards/update-position/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrfToken
                        },
                        body: JSON.stringify({
                            card_id: parseInt(cardId),
                            list_id: parseInt(newListId),
                            position: (newPosition + 1) * 10
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        console.log('Tarjeta movida correctamente en DB');
                        evt.item.style.opacity = '1';
                    } else {
                        console.error('Error:', data.error);
                        location.reload();
                    }
                } catch (error) {
                    console.error('Error en petición:', error);
                    location.reload();
                }
            }
        });
    });
}

/**
 * Establece la conexión del WebSocket para sincronizar las acciones del tablero en tiempo real.
 */
function conectarWebSocketTablero() {
    // Extraer el ID del tablero directamente desde la URL actual (/boards/[id]/)
    const urlParts = window.location.pathname.split('/');
    const boardId = urlParts[urlParts.indexOf('boards') + 1];
    
    if (!boardId) {
        console.log('No se pudo identificar el ID del tablero desde la URL');
        return;
    }
    
    const wsScheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const wsUrl = `${wsScheme}://${window.location.host}/ws/board/${boardId}/`;
    
    boardSocket = new WebSocket(wsUrl);
    
    boardSocket.onopen = function() {
        console.log(`✅ Conectado en tiempo real al canal del tablero: ${boardId}`);
    };
    
    boardSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        console.log('📨 Evento de tablero recibido:', data);
        
        // 💡 CASO 1: Alguien más (o tú mismo) creó una tarjeta en este tablero
        if (data.type === 'card_created_live') {
            renderizarNuevaTarjetaEnVivo(data.data);
        }
        
        // 💡 CASO 2: Alguien más movió una tarjeta dentro de este tablero
        if (data.type === 'card_moved') {
            moverTarjetaEnVivo(data.data);
        }
    };
    
    boardSocket.onerror = function(error) {
        console.error('❌ Error en WebSocket del Tablero:', error);
    };
    
    boardSocket.onclose = function() {
        console.log('🔌 WebSocket del Tablero desconectado. Reintentando en 5 segundos...');
        setTimeout(conectarWebSocketTablero, 5000);
    };
}

/**
 * Captura el envío de los formularios de creación de tarjetas para procesarlos por AJAX.
 */
function inicializarFormulariosTarjetas() {
    document.addEventListener('submit', async function(e) {
        const form = e.target.closest('.js-create-card-form');
        if (!form) return;
        
        // Detener el comportamiento por defecto que recarga la página
        e.preventDefault();
        
        const listId = form.dataset.formListId;
        const url = form.action;
        const formData = new FormData(form);
        
        try {
            const response = await fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                console.log('Tarjeta procesada por AJAX con éxito');
                
                // Limpiar los inputs del formulario
                form.reset();
                
                // Ocultar el modal de Bootstrap dinámicamente sin romper el DOM
                const modalElement = document.getElementById(`addCardModal${listId}`);
                if (modalElement) {
                    const modalInstance = bootstrap.Modal.getInstance(modalElement);
                    if (modalInstance) {
                        modalInstance.hide();
                    }
                }
            } else {
                alert('Error al crear la tarea: ' + (data.error || 'Ocurrió un problema inesperado'));
            }
        } catch (error) {
            console.error('Error enviando el formulario por AJAX:', error);
        }
    });
}

/**
 * Inserta de manera dinámica la nueva tarjeta en la columna correspondiente sin refrescar.
 */
function renderizarNuevaTarjetaEnVivo(cardData) {
    // Buscamos el contenedor de tarjetas específico usando el atributo data-list-id
    const contenedorLista = document.querySelector(`.kanban-list[data-list-id="${cardData.list_id}"]`);
    if (!contenedorLista) return;
    
    // Buscamos la caja interna donde se agrupan los items
    const contenedorTarjetas = contenedorLista.querySelector('.cards-container');
    if (!contenedorTarjetas) return;
    
    // Validar si la tarjeta ya fue añadida por el usuario que la creó (para evitar duplicados)
    if (document.querySelector(`[data-card-id="${cardData.card_id}"]`)) return;
    
    // 1. Remover el placeholder de "No hay tareas" si es que existe en la lista
    const placeholder = contenedorTarjetas.querySelector(`.empty-placeholder-${cardData.list_id}`);
    if (placeholder) {
        placeholder.remove();
    }
    
    // 2. Construcción del HTML clónando exactamente la misma estructura y clases de tu board_detail.html
    const nuevaTarjetaHtml = `
        <div class="card-item" data-card-id="${cardData.card_id}" data-position="${cardData.position || 0}">
            <div class="card-title">
                <span>${escapeHtml(cardData.title)}</span>
                <div class="card-actions">
                    <a href="/boards/cards/${cardData.card_id}/edit/" class="btn btn-sm btn-link text-secondary">
                        <i class="fas fa-edit fa-xs"></i>
                    </a>
                    <form method="POST" action="/boards/cards/${cardData.card_id}/delete/" style="display: inline;">
                        <input type="hidden" name="csrfmiddlewaretoken" value="${obtenerCsrfToken()}">
                        <button type="submit" class="btn btn-sm btn-link text-danger" onclick="return confirm('¿Eliminar esta tarea?');">
                            <i class="fas fa-trash-alt fa-xs"></i>
                        </button>
                    </form>
                </div>
            </div>
            ${cardData.description ? `<div class="card-description">${escapeHtml(truncateChars(cardData.description, 60))}</div>` : ''}
            <div class="card-footer">
                <div>
                    <span class="priority-badge priority-${cardData.priority || 'medium'}"></span>
                    <small>${mapearPrioridadTexto(cardData.priority)}</small>
                </div>
                <small>
                    <i class="fas fa-user me-1"></i>
                    ${escapeHtml(cardData.created_by)}
                </small>
            </div>
        </div>
    `;
    
    // Inyectar al final de la lista
    contenedorTarjetas.insertAdjacentHTML('beforeend', nuevaTarjetaHtml);
    
    // 3. Incrementar el contador (badge) de la cabecera de la lista
    const badgeContador = document.getElementById(`list-badge-${cardData.list_id}`);
    if (badgeContador) {
        let cantidadActual = parseInt(badgeContador.textContent) || 0;
        badgeContador.textContent = cantidadActual + 1;
    }
    
    // 🔥 CRÍTICO: Como es un elemento HTML nuevo, re-inicializamos Sortable para que responda al Drag & Drop
    inicializarSortable();
}

/**
 * Mueve visualmente una tarjeta existente cuando otro usuario la cambia de lugar.
 */
function moverTarjetaEnVivo(moveData) {
    const tarjeta = document.querySelector(`[data-card-id="${moveData.card_id}"]`);
    const destinoLista = document.querySelector(`[data-list-id="${moveData.list_id}"] .cards-container`);
    
    if (tarjeta && destinoLista) {
        // Desvanecimiento suave para el movimiento
        tarjeta.style.opacity = '0';
        
        setTimeout(() => {
            // Mover el nodo HTML hacia el contenedor de la nueva lista
            destinoLista.appendChild(tarjeta);
            tarjeta.style.opacity = '1';
            console.log(`Sincronizado: Tarjeta ${moveData.card_id} movida por ${moveData.moved_by}`);
        }, 200);
    }
}

/**
 * Funciones auxiliares necesarias para el renderizado dinámico y seguridad
 */
function obtenerCsrfToken() {
    let token = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    if (!token) {
        token = document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1];
    }
    return token || '';
}

function truncateChars(str, n) {
    return (str.length > n) ? str.substr(0, n - 1) + '...' : str;
}

// Vincula las clases de prioridad de Django con sus etiquetas legibles
function mapearPrioridadTexto(priority) {
    const prioridades = {
        'low': 'Baja',
        'medium': 'Media',
        'high': 'Alta',
        'urgent': 'Urgente'
    };
    return prioridades[priority] || 'Media';
}

/**
 * Función auxiliar para sanitizar textos y evitar ataques XSS al inyectar HTML.
 */
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}