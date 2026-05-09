"""
import_plik.py – Widok przesyłania pliku CSV i importu danych (Punkt 4c).
"""
import csv
import io
from django.contrib import messages
from django.shortcuts import render
from ..forms import ImportPlikuForm
from ..models import Lekarz, Pacjent, Specjalizacja


def import_plik(request):
    form   = ImportPlikuForm()
    wyniki = None

    if request.method == 'POST':
        form = ImportPlikuForm(request.POST, request.FILES)
        if form.is_valid():
            plik          = request.FILES['plik']
            typ           = form.cleaned_data['typ_danych']
            sep           = form.cleaned_data['separator']
            tylko_podglad = form.cleaned_data['tylko_podglad']

            try:
                zawartosc = plik.read()
                tekst = None
                for kodowanie in ('utf-8-sig', 'utf-8', 'windows-1250', 'iso-8859-2'):
                    try:
                        tekst = zawartosc.decode(kodowanie)
                        break
                    except UnicodeDecodeError:
                        continue

                if tekst is None:
                    messages.error(request, 'Nie można odczytać pliku. Zapisz go jako UTF-8.')
                else:
                    reader  = csv.DictReader(io.StringIO(tekst), delimiter=sep)
                    wiersze = list(reader)

                    if not wiersze:
                        messages.warning(request, 'Plik jest pusty lub nie ma danych po nagłówku.')
                    else:
                        podglad = wiersze[:5]
                        kolumny = list(podglad[0].keys()) if podglad else []

                        if tylko_podglad:
                            wyniki = {
                                'tryb': 'podglad', 'kolumny': kolumny,
                                'podglad': podglad, 'lacznie_wierszy': len(wiersze), 'typ': typ,
                            }
                            messages.info(request,
                                f'Podgląd: {len(wiersze)} wierszy, {len(kolumny)} kolumn. '
                                f'Odznacz "Tylko podgląd" aby zapisać dane.')
                        else:
                            wyniki = _importuj(wiersze, typ)
                            wyniki['kolumny'] = kolumny
                            wyniki['podglad'] = podglad
                            if wyniki['dodane'] > 0:
                                messages.success(request,
                                    f'Import: {wyniki["dodane"]} dodanych, '
                                    f'{wyniki["pominietych"]} pominiętych, '
                                    f'{len(wyniki["bledy"])} błędów.')
                            else:
                                messages.warning(request, 'Nie dodano żadnych nowych rekordów.')

            except Exception as e:
                messages.error(request, f'Błąd: {e}')

    return render(request, 'wizytownik/eksport/import_plik.html', {'form': form, 'wyniki': wyniki})


def _importuj(wiersze, typ):
    dodane, pominietych, bledy = 0, 0, []
    for nr, wiersz in enumerate(wiersze, start=2):
        try:
            if typ == 'pacjenci':
                email = wiersz.get('email', '').strip()
                if not email:
                    bledy.append(f'Wiersz {nr}: brak e-maila'); continue
                _, created = Pacjent.objects.get_or_create(
                    email=email,
                    defaults={
                        'imie':     wiersz.get('imie', '').strip() or 'Nieznane',
                        'nazwisko': wiersz.get('nazwisko', '').strip() or 'Nieznane',
                        'telefon':  wiersz.get('telefon', '').strip(),
                    }
                )
            elif typ == 'lekarze':
                imie     = wiersz.get('imie', '').strip()
                nazwisko = wiersz.get('nazwisko', '').strip()
                if not imie or not nazwisko:
                    bledy.append(f'Wiersz {nr}: brak imienia lub nazwiska'); continue
                spec, _ = Specjalizacja.objects.get_or_create(
                    nazwa=wiersz.get('specjalizacja', 'Internista').strip(),
                    defaults={'opis': 'Importowana specjalizacja'}
                )
                _, created = Lekarz.objects.get_or_create(
                    imie=imie, nazwisko=nazwisko,
                    defaults={
                        'specjalizacja': spec,
                        'tytul':         wiersz.get('tytul', 'lek. med.').strip(),
                        'miasto':        wiersz.get('miasto', 'Warszawa').strip(),
                        'opis':          wiersz.get('opis', 'Lekarz specjalista.').strip(),
                        'cena_wizyty':   float(wiersz.get('cena_wizyty', 150) or 150),
                    }
                )
            else:
                created = False
            if created:
                dodane += 1
            else:
                pominietych += 1
        except Exception as e:
            bledy.append(f'Wiersz {nr}: {e}')
            pominietych += 1

    return {
        'tryb': 'import', 'dodane': dodane,
        'pominietych': pominietych, 'bledy': bledy[:20],
        'lacznie_wierszy': len(wiersze),
    }
