"""
zaladuj_dane.py – Komenda Django do załadowania przykładowych danych.

Użycie:
    python manage.py zaladuj_dane           # dodaje dane
    python manage.py zaladuj_dane --wyczysc # usuwa stare dane i dodaje nowe
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, time, timedelta
from wizytownik.models import Specjalizacja, Lekarz, Pacjent, Wizyta
import random


class Command(BaseCommand):
    help = 'Ładuje przykładowe dane: specjalizacje, lekarzy, pacjentów i wizyty'

    def add_arguments(self, parser):
        parser.add_argument(
            '--wyczysc',
            action='store_true',
            help='Usuń istniejące dane przed załadowaniem nowych',
        )

    def handle(self, *args, **options):
        if options['wyczysc']:
            self.stdout.write('🗑️  Usuwam stare dane...')
            Wizyta.objects.all().delete()
            Pacjent.objects.all().delete()
            Lekarz.objects.all().delete()
            Specjalizacja.objects.all().delete()

        self.stdout.write('📋 Tworzę specjalizacje...')
        specjalizacje = self._stworz_specjalizacje()

        self.stdout.write('👨‍⚕️ Tworzę lekarzy...')
        lekarze = self._stworz_lekarzy(specjalizacje)

        self.stdout.write('🧑 Tworzę pacjentów...')
        pacjenci = self._stworz_pacjentow()

        self.stdout.write('📅 Tworzę przykładowe wizyty...')
        self._stworz_wizyty(lekarze, pacjenci)

        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Gotowe! Załadowano:\n'
            f'   • {Specjalizacja.objects.count()} specjalizacji\n'
            f'   • {Lekarz.objects.count()} lekarzy\n'
            f'   • {Pacjent.objects.count()} pacjentów\n'
            f'   • {Wizyta.objects.count()} wizyt\n'
        ))

    # ── Specjalizacje ──────────────────────────────────────────────────────
    def _stworz_specjalizacje(self):
        dane = [
            ('Kardiolog',        'Diagnozuje i leczy choroby serca i układu krążenia.',          'fa-heart',           'danger'),
            ('Dermatolog',       'Zajmuje się chorobami skóry, włosów i paznokci.',              'fa-hand-dots',       'warning'),
            ('Neurolog',         'Leczy schorzenia układu nerwowego i mózgu.',                   'fa-brain',           'info'),
            ('Okulista',         'Diagnozuje i leczy choroby oczu i wady wzroku.',               'fa-eye',             'primary'),
            ('Ortopeda',         'Zajmuje się układem kostno-stawowym i urazami.',               'fa-bone',            'secondary'),
            ('Pediatra',         'Specjalista ds. zdrowia dzieci i młodzieży.',                  'fa-baby',            'success'),
            ('Psychiatra',       'Diagnozuje i leczy zaburzenia psychiczne.',                    'fa-brain',           'dark'),
            ('Internista',       'Lekarz ogólny zajmujący się chorobami wewnętrznymi.',          'fa-stethoscope',     'primary'),
        ]
        wynik = {}
        for nazwa, opis, ikona, kolor in dane:
            spec, _ = Specjalizacja.objects.get_or_create(
                nazwa=nazwa,
                defaults={'opis': opis, 'ikona_fa': ikona, 'kolor_karty': kolor}
            )
            wynik[nazwa] = spec
        return wynik

    # ── Lekarze ────────────────────────────────────────────────────────────
    def _stworz_lekarzy(self, spec):
        dane = [
            # (imię, nazwisko, tytuł, płeć, spec, doświadczenie, ocena, opinie, godz, dni, czas, gabinet, miasto, adres, cena, opis)
            ('Anna',    'Kowalska',  'dr n. med.', 'K', 'Kardiolog',  15, 4.9, 213,
             '08:00-14:00', '12345', 30, '101', 'Warszawa', 'ul. Złota 44, 00-120 Warszawa', 200,
             'Specjalista kardiologii interwencyjnej. Absolwentka Warszawskiego Uniwersytetu Medycznego. '
             'Wykonuje echokardiografię, EKG wysiłkowe oraz Holter. Autorka licznych publikacji naukowych.'),

            ('Piotr',   'Nowak',     'lek. med.',  'M', 'Kardiolog',   8, 4.7, 156,
             '10:00-16:00', '12345', 30, '102', 'Warszawa', 'ul. Złota 44, 00-120 Warszawa', 180,
             'Młody, zaangażowany kardiolog. Specjalizuje się w profilaktyce chorób sercowo-naczyniowych '
             'i leczeniu nadciśnienia tętniczego. Przyjazne podejście do pacjenta.'),

            ('Marta',   'Wiśniewska','dr hab.', 'K', 'Dermatolog',  20, 4.8, 301,
             '08:00-14:00', '12345', 20, '205', 'Kraków', 'Al. Krasińskiego 10, 31-111 Kraków', 220,
             'Doświadczona dermatolog z tytułem doktora habilitowanego. Specjalizuje się w dermatologii '
             'estetycznej, leczeniu trądziku i łuszczycy. Wieloletnia praktyka w klinikach w Polsce i Niemczech.'),

            ('Tomasz',  'Kowalczyk', 'lek. med.',  'M', 'Dermatolog',   5, 4.5,  89,
             '12:00-18:00', '12345', 20, '206', 'Kraków', 'Al. Krasińskiego 10, 31-111 Kraków', 160,
             'Dermatolog ze specjalizacją w onkologii skóry. Wykonuje dermatoskopię znamion '
             'i wczesne wykrywanie czerniaka. Pracuje z najnowszym sprzętem diagnostycznym.'),

            ('Katarzyna','Lewandowska','prof. dr hab.','K','Neurolog',  28, 5.0, 478,
             '08:00-14:00', '1235', 45, '310', 'Warszawa', 'ul. Banacha 1A, 02-097 Warszawa', 300,
             'Profesor neurologii, kierownik Katedry Neurologii WUM. Ekspert w leczeniu stwardnienia '
             'rozsianego, migreny i choroby Parkinsona. Autorka podręcznika akademickiego z neurologii.'),

            ('Marek',   'Zielński',  'dr n. med.', 'M', 'Okulista',    12, 4.6, 187,
             '10:00-16:00', '12345', 30, '115', 'Wrocław', 'ul. Świdnicka 12, 50-068 Wrocław', 170,
             'Okulista z szerokim doświadczeniem w diagnostyce i leczeniu jaskry, zaćmy i AMD. '
             'Wykonuje badania pola widzenia, OCT i angiografię fluoresceinową.'),

            ('Joanna',  'Adamczyk',  'lek. med.',  'K', 'Ortopeda',     9, 4.7, 134,
             '08:00-14:00', '12345', 30, '220', 'Poznań', 'ul. Długa 1/2, 61-848 Poznań', 190,
             'Ortopeda specjalizujący się w schorzeniach kręgosłupa i stawu kolanowego. '
             'Stosuje nowoczesne metody leczenia zachowawczego i kwalifikuje do zabiegów operacyjnych.'),

            ('Michał',  'Dąbrowski',  'dr n. med.', 'M', 'Pediatra',    11, 4.9, 392,
             '08:00-14:00', '12345', 20, '012', 'Warszawa', 'ul. Marszałkowska 24, 00-576 Warszawa', 150,
             'Pediatra z pasją do pracy z dziećmi. Specjalizuje się w alergologii dziecięcej '
             'i chorobach układu oddechowego. Serdeczne i spokojne podejście do małych pacjentów.'),

            ('Ewa',     'Szymańska',  'lek. med.',  'K', 'Psychiatra',  14, 4.8, 241,
             '10:00-16:00', '1234', 60, '401', 'Warszawa', 'ul. Nowy Świat 15, 00-029 Warszawa', 250,
             'Psychiatra i psychoterapeuta. Specjalizuje się w leczeniu depresji, zaburzeń lękowych '
             'i ADHD u dorosłych. Stosuje podejście integratywne łącząc farmakoterapię z psychoterapią.'),

            ('Robert',  'Wójcik',     'lek. med.',  'M', 'Internista',   6, 4.4, 112,
             '14:00-20:00', '12345', 30, '050', 'Gdańsk', 'ul. Długa 9, 80-827 Gdańsk', 140,
             'Internista przyjmujący wieczorami – idealny dla pracujących. Diagnostyka ogólna, '
             'choroby metaboliczne, cukrzyca, nadciśnienie. Wystawia skierowania do specjalistów.'),

            ('Barbara', 'Piotrowska', 'dr n. med.', 'K', 'Internista',  18, 4.7, 267,
             '08:00-14:00', '12345', 30, '051', 'Gdańsk', 'ul. Długa 9, 80-827 Gdańsk', 160,
             'Internistka z dużym doświadczeniem klinicznym. Kompleksowa diagnostyka, choroby tarczycy, '
             'anemia, zaburzenia lipidowe. Holistyczne podejście do zdrowia pacjenta.'),
        ]

        lekarze = []
        for (imie, nazwisko, tytul, plec, spec_nazwa, dosw, ocena, opinie,
             godz, dni, czas, gabinet, miasto, adres, cena, opis) in dane:
            l, _ = Lekarz.objects.get_or_create(
                imie=imie, nazwisko=nazwisko,
                defaults={
                    'tytul': tytul, 'plec': plec,
                    'specjalizacja': spec[spec_nazwa],
                    'doswiadczenie_lat': dosw, 'opis': opis,
                    'ocena': ocena, 'liczba_opinii': opinie,
                    'godz_pracy': godz, 'dni_pracy': dni,
                    'czas_wizyty_min': czas, 'nr_gabinetu': gabinet,
                    'miasto': miasto, 'adres': adres,
                    'cena_wizyty': cena, 'aktywny': True,
                }
            )
            lekarze.append(l)
        return lekarze

    # ── Pacjenci ───────────────────────────────────────────────────────────
    def _stworz_pacjentow(self):
        dane = [
            ('Jan',       'Kowalski',    'jan.kowalski@gmail.com',       '501-234-567', date(1985, 3, 14)),
            ('Maria',     'Nowak',       'maria.nowak@wp.pl',            '602-345-678', date(1992, 7, 22)),
            ('Grzegorz',  'Wiśniewski',  'g.wisniewski@onet.pl',         '503-456-789', date(1978, 11,  5)),
            ('Agnieszka', 'Wróbel',      'agnieszka.wrobel@gmail.com',   '604-567-890', date(1995, 2, 18)),
            ('Krzysztof', 'Mazur',       'k.mazur@interia.pl',           '505-678-901', date(1969, 9, 30)),
            ('Zofia',     'Krawczyk',    'zofia.krawczyk@wp.pl',         '606-789-012', date(2001, 4, 12)),
            ('Andrzej',   'Ptak',        'andrzej.ptak@gmail.com',       '507-890-123', date(1955, 12, 1)),
            ('Monika',    'Grabowska',   'monika.grabowska@onet.pl',     '608-901-234', date(1988, 6, 25)),
        ]
        pacjenci = []
        for imie, nazwisko, email, tel, dob in dane:
            p, _ = Pacjent.objects.get_or_create(
                email=email,
                defaults={'imie': imie, 'nazwisko': nazwisko,
                          'telefon': tel, 'data_urodzenia': dob}
            )
            pacjenci.append(p)
        return pacjenci

    # ── Wizyty ─────────────────────────────────────────────────────────────
    def _stworz_wizyty(self, lekarze, pacjenci):
        dzisiaj = date.today()
        statusy_przeszle = ['odbyta', 'odbyta', 'odbyta', 'anulowana']

        created = 0
        for _ in range(40):
            lekarz = random.choice(lekarze)
            pacjent = random.choice(pacjenci)
            delta = random.randint(-30, 30)
            wizyta_data = dzisiaj + timedelta(days=delta)

            # Sprawdź dzień roboczy
            if str(wizyta_data.isoweekday()) not in lekarz.dni_pracy:
                continue

            sloty = lekarz.dostepne_sloty(wizyta_data)
            if not sloty:
                continue

            godzina = random.choice(sloty)
            status = random.choice(statusy_przeszle) if delta < 0 else 'oczekujaca'

            try:
                Wizyta.objects.create(
                    lekarz=lekarz, pacjent=pacjent,
                    data=wizyta_data, godzina=godzina, status=status,
                    powod_wizyty='Przykładowa wizyta.'
                )
                created += 1
            except Exception:
                pass  # unique_together może odrzucić duplikat
        self.stdout.write(f'   Stworzono {created} wizyt.')
