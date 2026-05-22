"""
context_processors.py – Procesory kontekstu.

Context processor to funkcja która Django wywołuje przy każdym
renderowaniu szablonu i dodaje do niego dodatkowe zmienne.

Dzięki temu zmienna {{ jest_adminem }} jest dostępna
w KAŻDYM szablonie bez konieczności przekazywania jej ręcznie.
"""
from django.conf import settings


def admin_status(request):
    """
    Dodaje do każdego szablonu zmienną {{ jest_adminem }}.

    True  – jeśli zalogowany użytkownik jest na liście ADMINZY w settings.py
    False – jeśli nie jest zalogowany lub nie jest adminem

    Jak zmienić kto jest adminem:
        Otwórz klinika_projekt/settings.py i edytuj listę ADMINZY:
        ADMINZY = ['admin', 'nowy_admin']   ← dodaj nową nazwę
        ADMINZY = ['admin']                 ← usuń żeby zabrać dostęp
    """
    jest_adminem = (
        request.user.is_authenticated and
        request.user.username in getattr(settings, 'ADMINZY', [])
    )
    return {'jest_adminem': jest_adminem}
