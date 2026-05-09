import json
from datetime import date, timedelta, time as time_type

from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from ..forms import MojeWizytyForm, PacjentForm, RezerwacjaForm, WyszukiwarkaLekarzaForm
from ..models import Lekarz, Pacjent, Specjalizacja, Wizyta
from ..paginacja import paginuj, zachowaj_parametry_get


def strona_glowna(request):
    specjalizacje = Specjalizacja.objects.all()
    statystyki = {
        'lekarze':       Lekarz.objects.filter(aktywny=True).count(),
        'specjalizacje': specjalizacje.count(),
        'wizyty':        Wizyta.objects.filter(status='odbyta').count(),
        'pacjenci':      Pacjent.objects.count(),
    }
    szukaj = request.GET.get('szukaj', '').strip()
    if szukaj:
        return redirect(f'/lekarze/?szukaj={szukaj}')
    return render(request, 'wizytownik/strona_glowna.html', {
        'specjalizacje': specjalizacje,
        'statystyki': statystyki,
    })


def lista_lekarzy(request):
    """Lista lekarzy z filtrowaniem (Punkt 5) i paginacją (Punkt 5)."""
    form = WyszukiwarkaLekarzaForm(request.GET or None)
    lekarze = Lekarz.objects.filter(aktywny=True).select_related('specjalizacja')

    if form.is_valid():
        szukaj        = form.cleaned_data.get('szukaj')
        specjalizacja = form.cleaned_data.get('specjalizacja')
        miasto        = form.cleaned_data.get('miasto')
        cena_max      = form.cleaned_data.get('cena_max')
        ocena_min     = form.cleaned_data.get('ocena_min')

        if szukaj:
            lekarze = lekarze.filter(
                Q(imie__icontains=szukaj) | Q(nazwisko__icontains=szukaj) |
                Q(specjalizacja__nazwa__icontains=szukaj) | Q(opis__icontains=szukaj)
            )
        if specjalizacja:
            lekarze = lekarze.filter(specjalizacja=specjalizacja)
        if miasto:
            lekarze = lekarze.filter(miasto__icontains=miasto)
        if cena_max is not None:
            lekarze = lekarze.filter(cena_wizyty__lte=cena_max)
        if ocena_min is not None:
            lekarze = lekarze.filter(ocena__gte=ocena_min)

    liczba_wynikow = lekarze.count()
    strona, na_strone = paginuj(lekarze, request, domyslna_na_strone=9)
    params_get = zachowaj_parametry_get(request)

    return render(request, 'wizytownik/lekarze/lista.html', {
        'lekarze':        strona,
        'form':           form,
        'liczba_wynikow': liczba_wynikow,
        'strona':         strona,
        'na_strone':      na_strone,
        'params_get':     params_get,
    })


def profil_lekarza(request, pk):
    lekarz = get_object_or_404(Lekarz, pk=pk, aktywny=True)
    dostepnosc = {}
    dzisiaj = date.today()
    for i in range(1, 15):
        d = dzisiaj + timedelta(days=i)
        dostepnosc[str(d)] = len(lekarz.dostepne_sloty(d))

    return render(request, 'wizytownik/lekarze/profil.html', {
        'lekarz':          lekarz,
        'form':            RezerwacjaForm(),
        'dostepnosc_json': json.dumps(dostepnosc),
        'ostatnie_wizyty': Wizyta.objects.filter(lekarz=lekarz, status='odbyta')
                           .select_related('pacjent').order_by('-data')[:5],
    })


def api_sloty(request, lekarz_pk):
    lekarz = get_object_or_404(Lekarz, pk=lekarz_pk)
    data_str = request.GET.get('data', '')
    try:
        wybrana_data = date.fromisoformat(data_str)
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Nieprawidłowa data'}, status=400)
    if wybrana_data < date.today() + timedelta(days=1):
        return JsonResponse({'sloty': [], 'komunikat': 'Ta data jest niedostępna.'})
    sloty = lekarz.dostepne_sloty(wybrana_data)
    return JsonResponse({'sloty': [s.strftime('%H:%M') for s in sloty], 'data': data_str})


def rezerwacja(request, lekarz_pk):
    lekarz = get_object_or_404(Lekarz, pk=lekarz_pk, aktywny=True)
    data_str    = request.GET.get('data')    or request.POST.get('data', '')
    godzina_str = request.GET.get('godzina') or request.POST.get('godzina', '')

    try:
        wybrana_data    = date.fromisoformat(data_str)
        h, m            = map(int, godzina_str.split(':'))
        wybrana_godzina = time_type(h, m)
    except (ValueError, TypeError, AttributeError):
        messages.error(request, 'Nieprawidłowy termin. Wybierz datę i godzinę ponownie.')
        return redirect('profil_lekarza', pk=lekarz_pk)

    if Wizyta.objects.filter(lekarz=lekarz, data=wybrana_data, godzina=wybrana_godzina,
                              status__in=['oczekujaca', 'potwierdzona']).exists():
        messages.warning(request, 'Ten termin właśnie został zarezerwowany. Wybierz inny.')
        return redirect('profil_lekarza', pk=lekarz_pk)

    if request.method == 'POST':
        form = PacjentForm(request.POST)
        if form.is_valid():
            pacjent, _ = Pacjent.objects.get_or_create(
                email=form.cleaned_data['email'],
                defaults={
                    'imie': form.cleaned_data['imie'],
                    'nazwisko': form.cleaned_data['nazwisko'],
                    'telefon': form.cleaned_data['telefon'],
                    'data_urodzenia': form.cleaned_data.get('data_urodzenia'),
                    'pesel': form.cleaned_data.get('pesel', ''),
                }
            )
            wizyta = Wizyta.objects.create(
                lekarz=lekarz, pacjent=pacjent,
                data=wybrana_data, godzina=wybrana_godzina,
                powod_wizyty=request.POST.get('powod_wizyty', ''),
                status='oczekujaca',
            )
            messages.success(request,
                f'Wizyta zarezerwowana! {lekarz} | {wybrana_data.strftime("%d.%m.%Y")} o {godzina_str}')
            return redirect('potwierdzenie_wizyty', wizyta_pk=wizyta.pk)
    else:
        form = PacjentForm()

    return render(request, 'wizytownik/wizyty/rezerwacja.html', {
        'lekarz': lekarz, 'form': form,
        'wybrana_data': wybrana_data, 'wybrana_godzina': godzina_str,
    })


def potwierdzenie_wizyty(request, wizyta_pk):
    return render(request, 'wizytownik/wizyty/potwierdzenie.html',
                  {'wizyta': get_object_or_404(Wizyta, pk=wizyta_pk)})


def moje_wizyty(request):
    form = MojeWizytyForm(request.GET or None)
    wizyty = strona = pacjent = None
    na_strone_val = 5
    params_get = ''

    if form.is_valid():
        email = form.cleaned_data['email']
        try:
            pacjent = Pacjent.objects.get(email=email)
            qs = (Wizyta.objects.filter(pacjent=pacjent)
                  .select_related('lekarz', 'lekarz__specjalizacja')
                  .order_by('-data', '-godzina'))
            strona, na_strone_val = paginuj(qs, request, domyslna_na_strone=5)
            wizyty = strona
            params_get = zachowaj_parametry_get(request)
        except Pacjent.DoesNotExist:
            messages.info(request, f'Nie znaleziono konta dla adresu {email}.')

    return render(request, 'wizytownik/wizyty/moje_wizyty.html', {
        'form': form, 'wizyty': wizyty, 'pacjent': pacjent,
        'strona': strona, 'na_strone': na_strone_val, 'params_get': params_get,
    })


def anuluj_wizyte(request, wizyta_pk):
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
