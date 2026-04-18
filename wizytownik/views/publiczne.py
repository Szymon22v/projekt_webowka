"""
publiczne.py – Widoki dla pacjentów.

Zawiera:
- strona_glowna()   – wyszukiwarka + kafelki specjalizacji
- lista_lekarzy()   – lista lekarzy z filtrowaniem
- profil_lekarza()  – profil lekarza + wybór terminu
- api_sloty()       – endpoint JSON ze slotami dla danej daty (używany przez JS)
- rezerwacja()      – formularz danych pacjenta + potwierdzenie
- moje_wizyty()     – podgląd wizyt po e-mailu
"""
import json
from datetime import date, timedelta, datetime

from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from ..forms import MojeWizytyForm, PacjentForm, RezerwacjaForm, WyszukiwarkaLekarzaForm
from ..models import Lekarz, Pacjent, Specjalizacja, Wizyta


# ══════════════════════════════════════════════════════════════════════════════
# STRONA GŁÓWNA
# ══════════════════════════════════════════════════════════════════════════════
def strona_glowna(request):
    """
    Główna strona portalu.
    Wyświetla wyszukiwarkę i kafelki specjalizacji.
    """
    specjalizacje = Specjalizacja.objects.all()
    # Statystyki dla sekcji z liczbami (animowane przez JS)
    statystyki = {
        'lekarze':    Lekarz.objects.filter(aktywny=True).count(),
        'specjalizacje': specjalizacje.count(),
        'wizyty':     Wizyta.objects.filter(status='odbyta').count(),
        'pacjenci':   Pacjent.objects.count(),
    }

    # Obsługa szybkiego wyszukiwania ze strony głównej
    szukaj = request.GET.get('szukaj', '').strip()
    if szukaj:
        # Przekieruj do listy lekarzy z parametrem wyszukiwania
        return redirect(f'/lekarze/?szukaj={szukaj}')

    return render(request, 'wizytownik/strona_glowna.html', {
        'specjalizacje': specjalizacje,
        'statystyki': statystyki,
    })


# ══════════════════════════════════════════════════════════════════════════════
# LISTA LEKARZY (z filtrowaniem – punkt 5)
# ══════════════════════════════════════════════════════════════════════════════
def lista_lekarzy(request):
    """
    Lista lekarzy z wyszukiwarką i filtrami.
    Wszystkie filtry w pasku adresu (GET), formularz auto-uzupełniony.
    """
    form = WyszukiwarkaLekarzaForm(request.GET or None)
    lekarze = Lekarz.objects.filter(aktywny=True).select_related('specjalizacja')

    if form.is_valid():
        szukaj = form.cleaned_data.get('szukaj')
        specjalizacja = form.cleaned_data.get('specjalizacja')
        miasto = form.cleaned_data.get('miasto')
        cena_max = form.cleaned_data.get('cena_max')
        ocena_min = form.cleaned_data.get('ocena_min')

        if szukaj:
            lekarze = lekarze.filter(
                Q(imie__icontains=szukaj) |
                Q(nazwisko__icontains=szukaj) |
                Q(specjalizacja__nazwa__icontains=szukaj) |
                Q(opis__icontains=szukaj)
            )
        if specjalizacja:
            lekarze = lekarze.filter(specjalizacja=specjalizacja)
        if miasto:
            lekarze = lekarze.filter(miasto__icontains=miasto)
        if cena_max is not None:
            lekarze = lekarze.filter(cena_wizyty__lte=cena_max)
        if ocena_min is not None:
            lekarze = lekarze.filter(ocena__gte=ocena_min)

    return render(request, 'wizytownik/lekarze/lista.html', {
        'lekarze': lekarze,
        'form': form,
        'liczba_wynikow': lekarze.count(),
    })


# ══════════════════════════════════════════════════════════════════════════════
# PROFIL LEKARZA + WYBÓR TERMINU
# ══════════════════════════════════════════════════════════════════════════════
def profil_lekarza(request, pk):
    """
    Profil lekarza z kalendarzem dostępnych terminów.
    Sloty godzinowe ładowane dynamicznie przez JavaScript (patrz api_sloty).
    """
    lekarz = get_object_or_404(Lekarz, pk=pk, aktywny=True)
    form_rezerwacja = RezerwacjaForm()

    # Przygotuj dostępność na najbliższe 14 dni (dla kalendarza JS)
    dostepnosc = {}
    dzisiaj = date.today()
    for i in range(1, 15):
        d = dzisiaj + timedelta(days=i)
        sloty = lekarz.dostepne_sloty(d)
        dostepnosc[str(d)] = len(sloty)   # liczba wolnych slotów

    # Inne wizyty u tego lekarza (do wyświetlenia opinii)
    ostatnie_wizyty = (
        Wizyta.objects
        .filter(lekarz=lekarz, status='odbyta')
        .select_related('pacjent')
        .order_by('-data')[:5]
    )

    return render(request, 'wizytownik/lekarze/profil.html', {
        'lekarz': lekarz,
        'form': form_rezerwacja,
        'dostepnosc_json': json.dumps(dostepnosc),
        'ostatnie_wizyty': ostatnie_wizyty,
        'dni_do_przodu': 60,
    })


# ══════════════════════════════════════════════════════════════════════════════
# API – dostępne sloty dla danej daty (zwraca JSON, używane przez JS)
# ══════════════════════════════════════════════════════════════════════════════
def api_sloty(request, lekarz_pk):
    """
    Endpoint JSON – zwraca listę wolnych godzin dla lekarza w wybranym dniu.
    Wywoływany przez JavaScript (fetch API) po wybraniu daty.
    Przykład odpowiedzi: {"sloty": ["08:00", "08:30", "09:30", ...]}
    """
    lekarz = get_object_or_404(Lekarz, pk=lekarz_pk)
    data_str = request.GET.get('data', '')

    try:
        wybrana_data = date.fromisoformat(data_str)
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Nieprawidłowa data'}, status=400)

    if wybrana_data < date.today() + timedelta(days=1):
        return JsonResponse({'sloty': [], 'komunikat': 'Ta data jest niedostępna.'})

    sloty = lekarz.dostepne_sloty(wybrana_data)
    sloty_str = [s.strftime('%H:%M') for s in sloty]

    return JsonResponse({
        'sloty': sloty_str,
        'data': data_str,
        'lekarz': str(lekarz),
    })


# ══════════════════════════════════════════════════════════════════════════════
# REZERWACJA WIZYTY
# ══════════════════════════════════════════════════════════════════════════════
def rezerwacja(request, lekarz_pk):
    """
    Dwuetapowy formularz rezerwacji:
    1. GET  – wyświetla formularz z danymi pacjenta
    2. POST – przetwarza dane, tworzy Pacjenta i Wizytę, przekierowuje do potwierdzenia
    """
    lekarz = get_object_or_404(Lekarz, pk=lekarz_pk, aktywny=True)

    # Pobierz datę i godzinę z parametrów URL (przekazane z profilu lekarza)
    data_str = request.GET.get('data') or request.POST.get('data', '')
    godzina_str = request.GET.get('godzina') or request.POST.get('godzina', '')

    # Walidacja terminu
    try:
        wybrana_data = date.fromisoformat(data_str)
        from datetime import time as time_type
        h, m = map(int, godzina_str.split(':'))
        wybrana_godzina = time_type(h, m)
    except (ValueError, TypeError, AttributeError):
        messages.error(request, 'Nieprawidłowy termin. Wybierz datę i godzinę ponownie.')
        return redirect('profil_lekarza', pk=lekarz_pk)

    # Sprawdź czy termin nadal wolny
    if Wizyta.objects.filter(lekarz=lekarz, data=wybrana_data, godzina=wybrana_godzina,
                              status__in=['oczekujaca', 'potwierdzona']).exists():
        messages.warning(request, 'Ten termin właśnie został zarezerwowany. Wybierz inny.')
        return redirect('profil_lekarza', pk=lekarz_pk)

    if request.method == 'POST':
        form = PacjentForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']

            # Sprawdź czy pacjent już istnieje (po emailu)
            pacjent, created = Pacjent.objects.get_or_create(
                email=email,
                defaults={
                    'imie':         form.cleaned_data['imie'],
                    'nazwisko':     form.cleaned_data['nazwisko'],
                    'telefon':      form.cleaned_data['telefon'],
                    'data_urodzenia': form.cleaned_data.get('data_urodzenia'),
                    'pesel':        form.cleaned_data.get('pesel', ''),
                }
            )

            # Utwórz wizytę
            wizyta = Wizyta.objects.create(
                lekarz=lekarz,
                pacjent=pacjent,
                data=wybrana_data,
                godzina=wybrana_godzina,
                powod_wizyty=request.POST.get('powod_wizyty', ''),
                status='oczekujaca',
            )

            messages.success(
                request,
                f'Wizyta zarezerwowana! {lekarz} | '
                f'{wybrana_data.strftime("%d.%m.%Y")} o {godzina_str}'
            )
            return redirect('potwierdzenie_wizyty', wizyta_pk=wizyta.pk)
    else:
        form = PacjentForm()

    return render(request, 'wizytownik/wizyty/rezerwacja.html', {
        'lekarz': lekarz,
        'form': form,
        'wybrana_data': wybrana_data,
        'wybrana_godzina': godzina_str,
    })


def potwierdzenie_wizyty(request, wizyta_pk):
    """Strona potwierdzenia po udanej rezerwacji."""
    wizyta = get_object_or_404(Wizyta, pk=wizyta_pk)
    return render(request, 'wizytownik/wizyty/potwierdzenie.html', {'wizyta': wizyta})


# ══════════════════════════════════════════════════════════════════════════════
# MOJE WIZYTY (wyszukiwanie po e-mailu)
# ══════════════════════════════════════════════════════════════════════════════
def moje_wizyty(request):
    """
    Pacjent wpisuje swój e-mail i widzi listę swoich wizyt.
    """
    form = MojeWizytyForm(request.GET or None)
    wizyty = None
    pacjent = None

    if form.is_valid():
        email = form.cleaned_data['email']
        try:
            pacjent = Pacjent.objects.get(email=email)
            wizyty = (
                Wizyta.objects
                .filter(pacjent=pacjent)
                .select_related('lekarz', 'lekarz__specjalizacja')
                .order_by('-data', '-godzina')
            )
        except Pacjent.DoesNotExist:
            messages.info(request, f'Nie znaleziono konta dla adresu {email}.')

    return render(request, 'wizytownik/wizyty/moje_wizyty.html', {
        'form': form,
        'wizyty': wizyty,
        'pacjent': pacjent,
    })


def anuluj_wizyte(request, wizyta_pk):
    """Pacjent anuluje własną wizytę (przez e-mail)."""
    wizyta = get_object_or_404(Wizyta, pk=wizyta_pk)
    if request.method == 'POST':
        if wizyta.status in ('oczekujaca', 'potwierdzona'):
            wizyta.status = 'anulowana'
            wizyta.save()
            messages.success(request, 'Wizyta została anulowana.')
        else:
            messages.warning(request, 'Nie można anulować tej wizyty.')
        return redirect(f'/wizyty/moje/?email={wizyta.pacjent.email}')
    return render(request, 'wizytownik/wizyty/anuluj.html', {'wizyta': wizyta})
