// Drag & Drop para mover tarjetas entre listas

document.addEventListener('DOMContentLoaded', function() {
    console.log('Drag & Drop inicializado');
    
    // Inicializar Sortable en todos los contenedores de tarjetas
    const containers = document.querySelectorAll('.cards-container');
    
    if (containers.length === 0) {
        console.log('No se encontraron contenedores de tarjetas');
        return;
    }
    
    containers.forEach(container => {
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
                
                if (!cardId || !newListId) return;
                
                console.log(`Moviendo tarjeta ${cardId} a lista ${newListId} posicion ${newPosition}`);
                
                // Mostrar indicador visual
                evt.item.style.opacity = '0.5';
                
                try {
                    // Obtener CSRF token
                    let csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
                    if (!csrfToken) {
                        csrfToken = document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1];
                    }
                    
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
                        console.log('Tarjeta movida correctamente');
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
});