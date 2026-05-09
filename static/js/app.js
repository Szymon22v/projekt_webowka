/**
 * app.js – Główny JS aplikacji KlinikaApp
 * JS Element #2 – Autocomplete wyszukiwarki
 */
'use strict';
document.addEventListener('DOMContentLoaded', function () {

    // Autocomplete – dynamiczne tworzenie podpowiedzi
    const searchInput = document.getElementById('hero-search');
    const suggestionsBox = document.getElementById('search-suggestions');

    if (searchInput && suggestionsBox && typeof specjalizacjeData !== 'undefined') {
        searchInput.addEventListener('input', function () {
            const query = this.value.trim().toLowerCase();
            suggestionsBox.innerHTML = '';
            if (query.length < 1) { suggestionsBox.style.display = 'none'; return; }

            const pasujace = specjalizacjeData.filter(s => s.toLowerCase().includes(query));
            if (!pasujace.length) { suggestionsBox.style.display = 'none'; return; }

            pasujace.forEach(spec => {
                const li = document.createElement('li');
                li.style.cssText = 'padding:.5rem 1rem;cursor:pointer;font-size:.9rem;';
                const idx = spec.toLowerCase().indexOf(query);
                li.innerHTML = spec.substring(0, idx) +
                    '<strong>' + spec.substring(idx, idx + query.length) + '</strong>' +
                    spec.substring(idx + query.length);
                li.addEventListener('mouseenter', () => li.style.background = '#eff6ff');
                li.addEventListener('mouseleave', () => li.style.background = '');
                li.addEventListener('mousedown', e => {
                    e.preventDefault();
                    searchInput.value = spec;
                    suggestionsBox.style.display = 'none';
                    searchInput.closest('form').submit();
                });
                suggestionsBox.appendChild(li);
            });
            suggestionsBox.style.display = 'block';
        });

        document.addEventListener('click', e => {
            if (!searchInput.contains(e.target)) suggestionsBox.style.display = 'none';
        });
    }

    // Bootstrap tooltips
    if (typeof bootstrap !== 'undefined') {
        document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => new bootstrap.Tooltip(el));
    }
});
