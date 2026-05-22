from datetime import date
from functools import wraps

from django.conf import settings
from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from ..forms import LekarzForm, SpecjalizacjaForm
from ..models import Lekarz, Pacjent, Specjalizacja, Wizyta
from ..paginacja import paginuj, zachowaj_parametry_get


# ── Dekorator sprawdzający czy użytkownik jest adminem ────────────────────────
def tylko_dla_admina(funkcja):
    """
    Dekorator chroniący widoki panelu.
    Sprawdza dwa warunki:
      1. Czy użytkownik jest zalogowany
      2. Czy jego nazwa jest na liście ADMINZY w settings.py

    Aby dodać admina: otwórz settings.py i dopisz nazwę do listy ADMINZY.
    Aby zabrać dostęp: usuń nazwę z listy ADMINZY.
    """
    @wraps(funkcja)
    def wrapper(request, *args, **kwargs):
        # Warunek 1: czy zalogowany?
        if not request.user.is_authenticated:
            messages.warning(request, 'Musisz być zalogowany, aby wejść do panelu.')
            return redirect(f'/logowanie/?next={request.path}')

        # Warunek 2: czy jest adminem?
        if request.user.username not in settings.ADMINZY:
            messages.error(
                request,
                'Nie masz uprawnień do panelu zarządzania. '
                'Skontaktuj się z administratorem.'
            )
            return redirect('strona_glowna')

        return funkcja(request, *args, **kwargs)
    return wrapper


# ── Panel główny ──────────────────────────────────────────────────────────────
@tylko_dla_admina
def panel(request):
    dzisiaj = date.today()
    return render(request, 'wizytownik/zarzadzanie/panel.html', {
        'liczba_lekarzy':    Lekarz.objects.filter(aktywny=True).count(),
        'liczba_pacjentow':  Pacjent.objects.count(),
        'wizyty_dzisiaj':    Wizyta.objects.filter(data=dzisiaj).count(),
        'wizyty_oczekujace': Wizyta.objects.filter(status='oczekujaca').count(),
        'ostatnie_wizyty':   Wizyta.objects.select_related('lekarz', 'pacjent')
                             .order_by('-data_rezerwacji')[:8],
        'specjalizacje':     Specjalizacja.objects.annotate(ile_lekarzy=Count('lekarze')),
        'statusy':           Wizyta._meta.get_field('status').choices,
    })


# ── Lekarze ───────────────────────────────────────────────────────────────────
@tylko_dla_admina
def dodaj_lekarza(request):
    if request.method == 'POST':
        form = LekarzForm(request.POST)
        if form.is_valid():
            lekarz = form.save()
            messages.success(request, f'Lekarz {lekarz.tytul_i_nazwisko} został dodany.')
            return redirect('panel')
    else:
        form = LekarzForm()
    return render(request, 'wizytownik/zarzadzanie/formularz_lekarza.html', {
        'form': form, 'akcja': 'Dodaj nowego lekarza', 'ikona': 'fa-user-plus',
    })


@tylko_dla_admina
def edytuj_lekarza(request, pk):
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
        'form': form, 'lekarz': lekarz, 'akcja': 'Edytuj dane lekarza', 'ikona': 'fa-user-pen',
    })


@tylko_dla_admina
def usun_lekarza(request, pk):
    lekarz = get_object_or_404(Lekarz, pk=pk)
    if request.method == 'POST':
        lekarz.aktywny = False
        lekarz.save()
        messages.success(request, f'Lekarz {lekarz} został dezaktywowany.')
        return redirect('panel')
    return render(request, 'wizytownik/zarzadzanie/potwierdz.html', {
        'obiekt': lekarz, 'typ': 'lekarza', 'powrot': 'panel',
    })


# ── Specjalizacje ─────────────────────────────────────────────────────────────
@tylko_dla_admina
def dodaj_specjalizacje(request):
    if request.method == 'POST':
        form = SpecjalizacjaForm(request.POST)
        if form.is_valid():
            spec = form.save()
            messages.success(request, f'Specjalizacja „{spec.nazwa}" dodana.')
            return redirect('panel')
    else:
        form = SpecjalizacjaForm()
    return render(request, 'wizytownik/zarzadzanie/formularz_specjalizacji.html', {'form': form})


# ── Lista wizyt ───────────────────────────────────────────────────────────────
@tylko_dla_admina
def lista_wizyt_admin(request):
    qs = Wizyta.objects.select_related(
        'lekarz', 'lekarz__specjalizacja', 'pacjent'
    ).order_by('-data', '-godzina')

    status_filter = request.GET.get('status', '')
    data_od       = request.GET.get('data_od', '')
    data_do       = request.GET.get('data_do', '')
    szukaj        = request.GET.get('szukaj', '')

    if status_filter:
        qs = qs.filter(status=status_filter)
    if data_od:
        qs = qs.filter(data__gte=data_od)
    if data_do:
        qs = qs.filter(data__lte=data_do)
    if szukaj:
        qs = qs.filter(
            Q(pacjent__nazwisko__icontains=szukaj) |
            Q(pacjent__email__icontains=szukaj)    |
            Q(lekarz__nazwisko__icontains=szukaj)
        )

    lacznie = qs.count()
    strona, na_strone = paginuj(qs, request, domyslna_na_strone=15)
    params_get = zachowaj_parametry_get(request)

    return render(request, 'wizytownik/zarzadzanie/lista_wizyt.html', {
        'wizyty':        strona,
        'status_filter': status_filter,
        'data_od':       data_od,
        'data_do':       data_do,
        'szukaj':        szukaj,
        'statusy':       Wizyta._meta.get_field('status').choices,
        'strona':        strona,
        'na_strone':     na_strone,
        'params_get':    params_get,
        'lacznie':       lacznie,
    })


@tylko_dla_admina
def zmien_status_wizyty(request, pk):
    wizyta = get_object_or_404(Wizyta, pk=pk)
    if request.method == 'POST':
        nowy_status = request.POST.get('status')
        dozwolone = [s[0] for s in Wizyta._meta.get_field('status').choices]
        if nowy_status in dozwolone:
            wizyta.status = nowy_status
            wizyta.save()
            messages.success(request, f'Status zmieniony na: {wizyta.get_status_display()}')
    return redirect('lista_wizyt_admin')
