from django.core.management.base import BaseCommand
from datetime import date, timedelta
from wizytownik.models import Specjalizacja, Lekarz, Pacjent, Wizyta
import random


class Command(BaseCommand):
    help = 'Ładuje przykładowe dane'

    def add_arguments(self, parser):
        parser.add_argument('--wyczysc', action='store_true')

    def handle(self, *args, **options):
        if options['wyczysc']:
            self.stdout.write('🗑️  Usuwam stare dane...')
            Wizyta.objects.all().delete()
            Pacjent.objects.all().delete()
            Lekarz.objects.all().delete()
            Specjalizacja.objects.all().delete()

        self.stdout.write('📋 Tworzę specjalizacje...')
        spec = self._specjalizacje()
        self.stdout.write('👨‍⚕️ Tworzę lekarzy...')
        lekarze = self._lekarze(spec)
        self.stdout.write('🧑 Tworzę pacjentów...')
        pacjenci = self._pacjenci()
        self.stdout.write('📅 Tworzę przykładowe wizyty...')
        self._wizyty(lekarze, pacjenci)

        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Gotowe! Załadowano:\n'
            f'   • {Specjalizacja.objects.count()} specjalizacji\n'
            f'   • {Lekarz.objects.count()} lekarzy\n'
            f'   • {Pacjent.objects.count()} pacjentów\n'
            f'   • {Wizyta.objects.count()} wizyt\n'
        ))

    def _specjalizacje(self):
        dane = [
            ('Kardiolog',  'Diagnozuje i leczy choroby serca.',         'fa-heart',       'danger'),
            ('Dermatolog', 'Zajmuje się chorobami skóry.',              'fa-hand-dots',   'warning'),
            ('Neurolog',   'Leczy schorzenia układu nerwowego.',        'fa-brain',       'info'),
            ('Okulista',   'Diagnozuje i leczy choroby oczu.',          'fa-eye',         'primary'),
            ('Ortopeda',   'Zajmuje się układem kostno-stawowym.',      'fa-bone',        'secondary'),
            ('Pediatra',   'Specjalista ds. zdrowia dzieci.',           'fa-baby',        'success'),
            ('Psychiatra', 'Diagnozuje zaburzenia psychiczne.',         'fa-brain',       'dark'),
            ('Internista', 'Lekarz chorób wewnętrznych.',               'fa-stethoscope', 'primary'),
        ]
        wynik = {}
        for nazwa, opis, ikona, kolor in dane:
            s, _ = Specjalizacja.objects.get_or_create(
                nazwa=nazwa, defaults={'opis': opis, 'ikona_fa': ikona, 'kolor_karty': kolor}
            )
            wynik[nazwa] = s
        return wynik

    def _lekarze(self, spec):
        dane = [
            ('Anna',    'Kowalska',  'dr n. med.', 'K', 'Kardiolog',  15, 4.9, 213, '08:00-14:00', '12345', 30, '101', 'Warszawa', 'ul. Złota 44, 00-120 Warszawa',            200, 'Specjalista kardiologii interwencyjnej. Wykonuje echokardiografię i EKG.'),
            ('Piotr',   'Nowak',     'lek. med.',  'M', 'Kardiolog',   8, 4.7, 156, '10:00-16:00', '12345', 30, '102', 'Warszawa', 'ul. Złota 44, 00-120 Warszawa',            180, 'Specjalizuje się w profilaktyce chorób sercowo-naczyniowych.'),
            ('Marta',   'Wiśniewska','dr hab.',    'K', 'Dermatolog', 20, 4.8, 301, '08:00-14:00', '12345', 20, '205', 'Kraków',   'Al. Krasińskiego 10, 31-111 Kraków',       220, 'Doświadczona dermatolog. Specjalizuje się w dermatologii estetycznej.'),
            ('Tomasz',  'Kowalczyk', 'lek. med.',  'M', 'Dermatolog',  5, 4.5,  89, '12:00-18:00', '12345', 20, '206', 'Kraków',   'Al. Krasińskiego 10, 31-111 Kraków',       160, 'Dermatolog ze specjalizacją w onkologii skóry.'),
            ('Katarzyna','Lewandowska','prof. dr hab.','K','Neurolog', 28, 5.0, 478, '08:00-14:00', '1235',  45, '310', 'Warszawa', 'ul. Banacha 1A, 02-097 Warszawa',          300, 'Profesor neurologii. Ekspert w leczeniu stwardnienia rozsianego.'),
            ('Marek',   'Zielński',  'dr n. med.', 'M', 'Okulista',   12, 4.6, 187, '10:00-16:00', '12345', 30, '115', 'Wrocław',  'ul. Świdnicka 12, 50-068 Wrocław',         170, 'Okulista z doświadczeniem w diagnostyce jaskry i zaćmy.'),
            ('Joanna',  'Adamczyk',  'lek. med.',  'K', 'Ortopeda',    9, 4.7, 134, '08:00-14:00', '12345', 30, '220', 'Poznań',   'ul. Długa 1/2, 61-848 Poznań',             190, 'Ortopeda specjalizujący się w schorzeniach kręgosłupa.'),
            ('Michał',  'Dąbrowski', 'dr n. med.', 'M', 'Pediatra',   11, 4.9, 392, '08:00-14:00', '12345', 20, '012', 'Warszawa', 'ul. Marszałkowska 24, 00-576 Warszawa',    150, 'Pediatra z pasją do pracy z dziećmi. Specjalizuje się w alergologii.'),
            ('Ewa',     'Szymańska', 'lek. med.',  'K', 'Psychiatra', 14, 4.8, 241, '10:00-16:00', '1234',  60, '401', 'Warszawa', 'ul. Nowy Świat 15, 00-029 Warszawa',       250, 'Psychiatra i psychoterapeuta. Specjalizuje się w leczeniu depresji.'),
            ('Robert',  'Wójcik',    'lek. med.',  'M', 'Internista',  6, 4.4, 112, '14:00-20:00', '12345', 30, '050', 'Gdańsk',   'ul. Długa 9, 80-827 Gdańsk',               140, 'Internista przyjmujący wieczorami – idealny dla pracujących.'),
            ('Barbara', 'Piotrowska','dr n. med.', 'K', 'Internista', 18, 4.7, 267, '08:00-14:00', '12345', 30, '051', 'Gdańsk',   'ul. Długa 9, 80-827 Gdańsk',               160, 'Internistka z dużym doświadczeniem. Holistyczne podejście do zdrowia.'),
        ]
        lekarze = []
        for (imie, nazwisko, tytul, plec, sn, dosw, ocena, opinie,
             godz, dni, czas, gab, miasto, adres, cena, opis) in dane:
            l, _ = Lekarz.objects.get_or_create(
                imie=imie, nazwisko=nazwisko,
                defaults={
                    'tytul': tytul, 'plec': plec, 'specjalizacja': spec[sn],
                    'doswiadczenie_lat': dosw, 'opis': opis,
                    'ocena': ocena, 'liczba_opinii': opinie,
                    'godz_pracy': godz, 'dni_pracy': dni, 'czas_wizyty_min': czas,
                    'nr_gabinetu': gab, 'miasto': miasto, 'adres': adres,
                    'cena_wizyty': cena, 'aktywny': True,
                }
            )
            lekarze.append(l)
        return lekarze

    def _pacjenci(self):
        dane = [
            ('Jan',       'Kowalski',   'jan.kowalski@gmail.com',     '501-234-567'),
            ('Maria',     'Nowak',      'maria.nowak@wp.pl',          '602-345-678'),
            ('Grzegorz',  'Wiśniewski', 'g.wisniewski@onet.pl',       '503-456-789'),
            ('Agnieszka', 'Wróbel',     'agnieszka.wrobel@gmail.com', '604-567-890'),
            ('Krzysztof', 'Mazur',      'k.mazur@interia.pl',         '505-678-901'),
            ('Zofia',     'Krawczyk',   'zofia.krawczyk@wp.pl',       '606-789-012'),
            ('Andrzej',   'Ptak',       'andrzej.ptak@gmail.com',     '507-890-123'),
            ('Monika',    'Grabowska',  'monika.grabowska@onet.pl',   '608-901-234'),
        ]
        pacjenci = []
        for imie, nazwisko, email, tel in dane:
            p, _ = Pacjent.objects.get_or_create(
                email=email, defaults={'imie': imie, 'nazwisko': nazwisko, 'telefon': tel}
            )
            pacjenci.append(p)
        return pacjenci

    def _wizyty(self, lekarze, pacjenci):
        dzisiaj = date.today()
        statusy = ['odbyta', 'odbyta', 'odbyta', 'anulowana']
        created = 0
        for _ in range(40):
            lekarz  = random.choice(lekarze)
            pacjent = random.choice(pacjenci)
            delta   = random.randint(-30, 30)
            d       = dzisiaj + timedelta(days=delta)
            if str(d.isoweekday()) not in lekarz.dni_pracy:
                continue
            sloty = lekarz.dostepne_sloty(d)
            if not sloty:
                continue
            status = random.choice(statusy) if delta < 0 else 'oczekujaca'
            try:
                Wizyta.objects.create(
                    lekarz=lekarz, pacjent=pacjent,
                    data=d, godzina=random.choice(sloty),
                    status=status, powod_wizyty='Przykładowa wizyta.'
                )
                created += 1
            except Exception:
                pass
        self.stdout.write(f'   Stworzono {created} wizyt.')
