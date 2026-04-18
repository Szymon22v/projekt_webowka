"""
zarzadzanie.py – Widoki panelu zarządzania (dla personelu kliniki).

Zawiera:
- panel()           – główna strona panelu ze statystykami
- dodaj_lekarza()   – formularz dodania nowego lekarza
- edytuj_lekarza()  – edycja istniejącego lekarza
- lista_wizyt_admin() – podgląd wszystkich wizyt ze zmianą statusu
- dodaj_specjalizacje() – formularz dodania specjalizacji
"""
from datetime import date

from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from ..forms import LekarzForm, SpecjalizacjaForm
from ..models import Lekarz, Pacjent, Specjalizacja, Wizyta


# ══════════════════════════════════════════════════════════════════════════════
# PANEL GŁÓWNY
# ══════════════════════════════════════════════════════════════════════════════
def panel(request):
    """Strona główna panelu administracyjnego z kafelkami statystyk."""
    dzisiaj = date.today()
    kontekst = {
        'liczba_lekarzy':     Lekarz.objects.filter(aktywny=True).count(),
        'liczba_pacjentow':   Pacjent.objects.count(),
        'wizyty_dzisiaj':     Wizyta.objects.filter(data=dzisiaj).count(),
        'wizyty_oczekujace':  Wizyta.objects.filter(status='oczekujaca').count(),
        'ostatnie_wizyty':    (
            Wizyta.objects
            .select_related('lekarz', 'pacjent')
            .order_by('-data_rezerwacji')[:8]
        ),
        'specjalizacje':      Specjalizacja.objects.annotate(
            ile_lekarzy=Count('lekarze')
        ),
    }
    return render(request, 'wizytownik/zarzadzanie/panel.html', kontekst)


# ══════════════════════════════════════════════════════════════════════════════
# ZARZĄDZANIE LEKARZAMI
# ══════════════════════════════════════════════════════════════════════════════
def dodaj_lekarza(request):
    """Formularz dodania nowego lekarza do bazy."""
    if request.method == 'POST':
        form = LekarzForm(request.POST)
        if form.is_valid():
            lekarz = form.save()
            messages.success(
                request,
                f'Lekarz {lekarz.tytul_i_nazwisko} został dodany pomyślnie.'
            )
            return redirect('panel')
    else:
        form = LekarzForm()
    return render(request, 'wizytownik/zarzadzanie/formularz_lekarza.html', {
        'form': form,
        'akcja': 'Dodaj nowego lekarza',
        'ikona': 'fa-user-plus',
    })


def edytuj_lekarza(request, pk):
    """Formularz edycji istniejącego lekarza."""
    lekarz = get_object_or_404(Lekarz, pk=pk)
    if request.method == 'POST':
        form = LekarzForm(request.POST, instance=lekarz)
        if form.is_valid():
            form.save()
            messages.success(request, f'Dane lekarza {lekarz} zostały zaktualizowane.')
            return redirect('panel')
    else:
        form = LekarzForm(instance=lekarz)
    return render(request, 'wizytownik/zarzadzanie/formularz_lekarza.html', {
        'form': form,
        'lekarz': lekarz,
        'akcja': 'Edytuj dane lekarza',
        'ikona': 'fa-user-pen',
    })


def usun_lekarza(request, pk):
    """Usunięcie (dezaktywacja) lekarza."""
    lekarz = get_object_or_404(Lekarz, pk=pk)
    if request.method == 'POST':
        # Zamiast usuwać – dezaktywuj (zachowujemy historię wizyt)
        lekarz.aktywny = False
        lekarz.save()
        messages.success(request, f'Lekarz {lekarz} został dezaktywowany.')
        return redirect('panel')
    return render(request, 'wizytownik/zarzadzanie/potwierdz.html', {
        'obiekt': lekarz,
        'typ': 'lekarza',
        'powrot': 'panel',
    })


# ══════════════════════════════════════════════════════════════════════════════
# ZARZĄDZANIE SPECJALIZACJAMI
# ══════════════════════════════════════════════════════════════════════════════
def dodaj_specjalizacje(request):
    """Formularz dodania nowej specjalizacji."""
    if request.method == 'POST':
        form = SpecjalizacjaForm(request.POST)
        if form.is_valid():
            spec = form.save()
            messages.success(request, f'Specjalizacja „{spec.nazwa}" dodana.')
            return redirect('panel')
    else:
        form = SpecjalizacjaForm()
    return render(request, 'wizytownik/zarzadzanie/formularz_specjalizacji.html', {
        'form': form
    })


# ══════════════════════════════════════════════════════════════════════════════
# LISTA WIZYT – PANEL ADMINA
# ══════════════════════════════════════════════════════════════════════════════
def lista_wizyt_admin(request):
    """
    Lista wszystkich wizyt z możliwością filtrowania i zmiany statusu.
    """
    wizyty = (
        Wizyta.objects
        .select_related('lekarz', 'lekarz__specjalizacja', 'pacjent')
        .order_by('-data', '-godzina')
    )

    # Filtrowanie
    status_filter = request.GET.get('status', '')
    data_od = request.GET.get('data_od', '')
    data_do = request.GET.get('data_do', '')
    szukaj = request.GET.get('szukaj', '')

    if status_filter:
        wizyty = wizyty.filter(status=status_filter)
    if data_od:
        wizyty = wizyty.filter(data__gte=data_od)
    if data_do:
        wizyty = wizyty.filter(data__lte=data_do)
    if szukaj:
        wizyty = wizyty.filter(
            Q(pacjent__nazwisko__icontains=szukaj) |
            Q(pacjent__email__icontains=szukaj) |
            Q(lekarz__nazwisko__icontains=szukaj)
        )

    return render(request, 'wizytownik/zarzadzanie/lista_wizyt.html', {
        'wizyty': wizyty,
        'status_filter': status_filter,
        'data_od': data_od,
        'data_do': data_do,
        'szukaj': szukaj,
        'statusy': Wizyta._meta.get_field('status').choices,
    })


def zmien_status_wizyty(request, pk):
    """Zmiana statusu wizyty (Ajax lub formularz POST)."""
    wizyta = get_object_or_404(Wizyta, pk=pk)
    if request.method == 'POST':
        nowy_status = request.POST.get('status')
        dozwolone = [s[0] for s in Wizyta._meta.get_field('status').choices]
        if nowy_status in dozwolone:
            wizyta.status = nowy_status
            wizyta.save()
            messages.success(request, f'Status wizyty zmieniony na: {wizyta.get_status_display()}')
    return redirect('lista_wizyt_admin')
