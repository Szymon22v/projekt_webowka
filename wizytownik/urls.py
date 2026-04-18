"""
urls.py – Definicje adresów URL aplikacji.

Każdy adres URL wskazuje na konkretny widok (funkcję w views/).
"""
from django.urls import path
from .views.publiczne import (
    strona_glowna, lista_lekarzy, profil_lekarza,
    api_sloty, rezerwacja, potwierdzenie_wizyty,
    moje_wizyty, anuluj_wizyte,
)
from .views.zarzadzanie import (
    panel, dodaj_lekarza, edytuj_lekarza, usun_lekarza,
    dodaj_specjalizacje, lista_wizyt_admin, zmien_status_wizyty,
)

urlpatterns = [
    # ── Strony dla pacjentów ──────────────────────────────────────────────
    path('',
         strona_glowna,
         name='strona_glowna'),

    path('lekarze/',
         lista_lekarzy,
         name='lista_lekarzy'),

    path('lekarze/<int:pk>/',
         profil_lekarza,
         name='profil_lekarza'),

    # Endpoint JSON – dostępne sloty dla lekarza w danym dniu
    path('lekarze/<int:lekarz_pk>/sloty/',
         api_sloty,
         name='api_sloty'),

    path('rezerwacja/<int:lekarz_pk>/',
         rezerwacja,
         name='rezerwacja'),

    path('rezerwacja/potwierdzenie/<int:wizyta_pk>/',
         potwierdzenie_wizyty,
         name='potwierdzenie_wizyty'),

    path('wizyty/moje/',
         moje_wizyty,
         name='moje_wizyty'),

    path('wizyty/<int:wizyta_pk>/anuluj/',
         anuluj_wizyte,
         name='anuluj_wizyte'),

    # ── Panel zarządzania ─────────────────────────────────────────────────
    path('panel/',
         panel,
         name='panel'),

    path('panel/dodaj-lekarza/',
         dodaj_lekarza,
         name='dodaj_lekarza'),

    path('panel/lekarze/<int:pk>/edytuj/',
         edytuj_lekarza,
         name='edytuj_lekarza'),

    path('panel/lekarze/<int:pk>/usun/',
         usun_lekarza,
         name='usun_lekarza'),

    path('panel/dodaj-specjalizacje/',
         dodaj_specjalizacje,
         name='dodaj_specjalizacje'),

    path('panel/wizyty/',
         lista_wizyt_admin,
         name='lista_wizyt_admin'),

    path('panel/wizyty/<int:pk>/status/',
         zmien_status_wizyty,
         name='zmien_status_wizyty'),
]
