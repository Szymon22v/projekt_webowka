from django.contrib import admin
from .models import Specjalizacja, Lekarz, Pacjent, Wizyta


@admin.register(Specjalizacja)
class SpecjalizacjaAdmin(admin.ModelAdmin):
    list_display = ['nazwa', 'ikona_fa', 'kolor_karty']
    search_fields = ['nazwa']


@admin.register(Lekarz)
class LekarzAdmin(admin.ModelAdmin):
    list_display = ['nazwisko', 'imie', 'tytul', 'specjalizacja', 'miasto', 'ocena', 'aktywny']
    list_filter = ['specjalizacja', 'aktywny', 'miasto']
    search_fields = ['imie', 'nazwisko']
    list_editable = ['aktywny']


@admin.register(Pacjent)
class PacjentAdmin(admin.ModelAdmin):
    list_display = ['nazwisko', 'imie', 'email', 'telefon', 'data_rejestracji']
    search_fields = ['imie', 'nazwisko', 'email']


@admin.register(Wizyta)
class WizytaAdmin(admin.ModelAdmin):
    list_display = ['lekarz', 'pacjent', 'data', 'godzina', 'status', 'data_rezerwacji']
    list_filter = ['status', 'data', 'lekarz__specjalizacja']
    search_fields = ['lekarz__nazwisko', 'pacjent__nazwisko', 'pacjent__email']
    list_editable = ['status']
    date_hierarchy = 'data'
