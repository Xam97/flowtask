// Theme management — dark/light/auto mode
const FlowTaskTheme = (function() {
    'use strict';

    const STORAGE_KEY = 'flowtask-theme';

    function resolveTheme(preference) {
        if (preference === 'auto') {
            return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        }
        return preference === 'dark' ? 'dark' : 'light';
    }

    function apply(preference) {
        const theme = resolveTheme(preference || localStorage.getItem(STORAGE_KEY) || 'light');
        document.documentElement.setAttribute('data-theme', theme);
    }

    function toggle() {
        const current = localStorage.getItem(STORAGE_KEY) || 'light';
        const resolved = resolveTheme(current);
        const next = resolved === 'dark' ? 'light' : 'dark';
        localStorage.setItem(STORAGE_KEY, next);
        apply(next);
        return next;
    }

    function init() {
        apply();

        const toggleBtn = document.getElementById('themeToggle');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', toggle);
        }

        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
            if ((localStorage.getItem(STORAGE_KEY) || 'light') === 'auto') {
                apply('auto');
            }
        });
    }

    document.addEventListener('DOMContentLoaded', init);

    return { apply, toggle, resolveTheme };
})();

window.FlowTaskTheme = FlowTaskTheme;
