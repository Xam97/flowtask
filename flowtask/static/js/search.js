// Global search with live dropdown
(function() {
    'use strict';

    document.addEventListener('DOMContentLoaded', () => {
        const input = document.getElementById('globalSearchInput');
        const dropdown = document.getElementById('searchDropdown');
        const form = document.getElementById('globalSearchForm');

        if (!input || !dropdown) return;

        const debouncedSearch = FlowTaskHelpers.debounce(async (query) => {
            if (query.length < 2) {
                dropdown.classList.remove('show');
                return;
            }

            try {
                const response = await fetch(`/boards/search/api/?q=${encodeURIComponent(query)}`, {
                    credentials: 'same-origin',
                });
                const data = await response.json();
                renderResults(data, query);
            } catch (e) {
                console.error('Search error:', e);
            }
        }, 300);

        input.addEventListener('input', () => debouncedSearch(input.value.trim()));
        input.addEventListener('focus', () => {
            if (input.value.trim().length >= 2) debouncedSearch(input.value.trim());
        });

        document.addEventListener('click', (e) => {
            if (!e.target.closest('.search-wrapper')) {
                dropdown.classList.remove('show');
            }
        });

        form.addEventListener('submit', (e) => {
            if (input.value.trim().length < 2) {
                e.preventDefault();
                FlowTaskHelpers.showToast('Escribe al menos 2 caracteres', 'error');
            }
        });
    });

    function renderResults(data, query) {
        const dropdown = document.getElementById('searchDropdown');
        if (!dropdown) return;

        const boards = data.boards || [];
        const cards = data.cards || [];

        if (boards.length === 0 && cards.length === 0) {
            dropdown.innerHTML = `<div class="search-empty">Sin resultados para "${FlowTaskHelpers.escapeHtml(query)}"</div>`;
            dropdown.classList.add('show');
            return;
        }

        let html = '';

        if (boards.length) {
            html += '<div class="search-dropdown-section"><h6>Tableros</h6>';
            boards.forEach(b => {
                html += `<a href="${b.url}" class="search-result-item">
                    <div class="search-result-icon board"><i class="fas fa-th-large"></i></div>
                    <div class="search-result-text"><strong>${FlowTaskHelpers.escapeHtml(b.name)}</strong></div>
                </a>`;
            });
            html += '</div>';
        }

        if (cards.length) {
            html += '<div class="search-dropdown-section"><h6>Tareas</h6>';
            cards.forEach(c => {
                html += `<a href="${c.url}" class="search-result-item">
                    <div class="search-result-icon card"><i class="fas fa-tasks"></i></div>
                    <div class="search-result-text">
                        <strong>${FlowTaskHelpers.escapeHtml(c.title)}</strong>
                        <small>${FlowTaskHelpers.escapeHtml(c.board_name)} · ${FlowTaskHelpers.escapeHtml(c.list_name)}</small>
                    </div>
                </a>`;
            });
            html += '</div>';
        }

        html += `<div class="search-dropdown-section" style="padding:0.5rem;text-align:center;">
            <a href="/boards/search/?q=${encodeURIComponent(query)}" style="font-size:0.75rem;color:var(--accent);">Ver todos los resultados</a>
        </div>`;

        dropdown.innerHTML = html;
        dropdown.classList.add('show');
    }
})();
