/**
 * app.js – Główny plik JavaScript aplikacji KlinikaApp
 *
 * Zawiera 3 wymagane elementy dynamiczne (Punkt 3):
 *
 * [1] Animowane liczniki statystyk na stronie głównej (scroll reveal + counter)
 * [2] Autocomplete w wyszukiwarce (dynamiczne tworzenie elementów listy)
 * [3] Dynamiczny wybór terminu (sloty) – w profil.html przez fetch API
 *     (kod w bloku extra_js szablonu profil.html – integruje się z danymi Django)
 *
 * Plus pomocnicze:
 * - Toasty / powiadomienia (inicjowane w base.html)
 * - Zmiana widoku listy lekarzy (grid/list) – w lista.html
 * - Animowane wejście kart specjalizacji (scroll reveal)
 */

'use strict';

document.addEventListener('DOMContentLoaded', function () {

    // ══ [1] ANIMOWANE LICZNIKI STATYSTYK (strona główna) ════════════════════
    //
    // Elementy .stat-item zawierają data-target="<liczba>".
    // IntersectionObserver uruchamia animację, gdy element staje się widoczny.
    // Liczba płynnie narasta od 0 do wartości docelowej.

    function animujLicznik(el, target, czas) {
        const startTime = performance.now();
        function tick(now) {
            const elapsed = now - startTime;
            const progress = Math.min(elapsed / czas, 1);
            // Easing: ease-out cubic
            const eased = 1 - Math.pow(1 - progress, 3);
            const current = Math.floor(eased * target);
            el.textContent = current.toLocaleString('pl-PL');
            if (progress < 1) requestAnimationFrame(tick);
        }
        requestAnimationFrame(tick);
    }

    const licznikObserver = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (entry.isIntersecting) {
                const numEl = entry.target.querySelector('.stat-number');
                const target = parseInt(entry.target.dataset.target, 10) || 0;
                if (numEl && target > 0) animujLicznik(numEl, target, 1400);
                licznikObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.6 });

    document.querySelectorAll('.stat-item[data-target]').forEach(function (el) {
        licznikObserver.observe(el);
    });


    // ══ [2] AUTOCOMPLETE WYSZUKIWARKI (strona główna) ═══════════════════════
    //
    // Gdy użytkownik pisze w #hero-search, dynamicznie tworzone są elementy <li>
    // w liście #search-suggestions pasujące do wpisanego tekstu.
    // Lista pochodzi z globalnej zmiennej `specjalizacjeData` wstrzykniętej przez Django.

    const searchInput = document.getElementById('hero-search');
    const suggestionsBox = document.getElementById('search-suggestions');

    if (searchInput && suggestionsBox && typeof specjalizacjeData !== 'undefined') {

        // Pozycjonuj box sugestii relatywnie do rodzica
        const parent = searchInput.closest('.search-container');
        if (parent) parent.style.position = 'relative';

        searchInput.addEventListener('input', function () {
            const query = this.value.trim().toLowerCase();
            suggestionsBox.innerHTML = '';   // wyczyść stare sugestie

            if (query.length < 1) {
                suggestionsBox.style.display = 'none';
                return;
            }

            const pasujace = specjalizacjeData.filter(function (s) {
                return s.toLowerCase().includes(query);
            });

            if (pasujace.length === 0) {
                suggestionsBox.style.display = 'none';
                return;
            }

            // Dynamicznie twórz elementy listy
            pasujace.forEach(function (spec) {
                const li = document.createElement('li');

                // Pogrub pasującą część tekstu
                const idx = spec.toLowerCase().indexOf(query);
                li.innerHTML =
                    spec.substring(0, idx) +
                    '<strong>' + spec.substring(idx, idx + query.length) + '</strong>' +
                    spec.substring(idx + query.length);

                li.addEventListener('mousedown', function (e) {
                    e.preventDefault();    // nie trać focusu z inputa
                    searchInput.value = spec;
                    suggestionsBox.style.display = 'none';
                    searchInput.closest('form').submit();
                });

                suggestionsBox.appendChild(li);
            });

            suggestionsBox.style.display = 'block';
        });

        // Ukryj sugestie po kliknięciu poza nimi
        document.addEventListener('click', function (e) {
            if (!searchInput.contains(e.target) && !suggestionsBox.contains(e.target)) {
                suggestionsBox.style.display = 'none';
            }
        });

        // Nawigacja klawiaturą po sugestiach
        searchInput.addEventListener('keydown', function (e) {
            const items = suggestionsBox.querySelectorAll('li');
            const active = suggestionsBox.querySelector('li.active');
            let idx = Array.from(items).indexOf(active);

            if (e.key === 'ArrowDown') {
                e.preventDefault();
                if (active) active.classList.remove('active');
                const next = items[Math.min(idx + 1, items.length - 1)];
                if (next) { next.classList.add('active'); searchInput.value = next.textContent; }
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                if (active) active.classList.remove('active');
                const prev = items[Math.max(idx - 1, 0)];
                if (prev) { prev.classList.add('active'); searchInput.value = prev.textContent; }
            } else if (e.key === 'Escape') {
                suggestionsBox.style.display = 'none';
            }
        });
    }


    // ══ Inicjalizacja Bootstrap Tooltips ════════════════════════════════════
    // Tooltips dla elementów z atrybutem data-bs-toggle="tooltip"
    if (typeof bootstrap !== 'undefined') {
        document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function (el) {
            new bootstrap.Tooltip(el);
        });
    }


    // ══ Animacja wejścia dla kart (ogólna) ═══════════════════════════════════
    // Klasa .fade-in-card – dodaj do dowolnych kart, które mają się animować
    const cardObserver = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry, i) {
            if (entry.isIntersecting) {
                const delay = entry.target.dataset.animDelay || (i * 60);
                setTimeout(function () {
                    entry.target.style.transition = 'opacity .45s ease, transform .45s ease';
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }, delay);
                cardObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.05 });

    document.querySelectorAll('.fade-in-card').forEach(function (el) {
        el.style.opacity = '0';
        el.style.transform = 'translateY(24px)';
        cardObserver.observe(el);
    });


    // ══ Automatyczne zamknięcie alertów po 5 sekundach ═══════════════════════
    setTimeout(function () {
        document.querySelectorAll('.alert-auto-close').forEach(function (el) {
            el.style.transition = 'opacity .4s';
            el.style.opacity = '0';
            setTimeout(function () { el.remove(); }, 400);
        });
    }, 5000);

});
