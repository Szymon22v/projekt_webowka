"""
models.py – Definicje tabel bazy danych.

Relacje między modelami:
    Specjalizacja  ──<  Lekarz  ──<  Wizyta  >──  Pacjent
    (1 do wielu)          (1 do wielu)       (wiele do wielu – przez Wizyta)

Każda strzałka ──< oznacza: jeden obiekt po lewej może mieć wiele obiektów po prawej.
"""
from django.db import models
from django.utils import timezone
from datetime import date, time, timedelta


# ══════════════════════════════════════════════════════════════════════════════
# MODEL 1: SPECJALIZACJA
# Przechowuje typy specjalizacji lekarskich (np. Kardiolog, Dermatolog).
# Jeden typ specjalizacji może mieć wielu lekarzy → relacja 1:N z Lekarz.
# ══════════════════════════════════════════════════════════════════════════════
class Specjalizacja(models.Model):
    nazwa = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Nazwa specjalizacji'
    )
    opis = models.TextField(
        verbose_name='Opis',
        help_text='Krótki opis czym zajmuje się ta specjalizacja'
    )
    # Klasa ikony Font Awesome, np. "fa-heart" dla kardiologa
    ikona_fa = models.CharField(
        max_length=60,
        default='fa-stethoscope',
        verbose_name='Ikona Font Awesome',
        help_text='Np. fa-heart, fa-eye, fa-brain'
    )
    kolor_karty = models.CharField(
        max_length=20,
        default='primary',
        verbose_name='Kolor Bootstrap',
        help_text='Np. primary, success, danger, warning, info'
    )

    class Meta:
        verbose_name = 'Specjalizacja'
        verbose_name_plural = 'Specjalizacje'
        ordering = ['nazwa']

    def __str__(self):
        return self.nazwa


# ══════════════════════════════════════════════════════════════════════════════
# MODEL 2: LEKARZ
# Profil lekarza. Każdy lekarz należy do jednej specjalizacji (ForeignKey).
# Jeden lekarz może mieć wiele wizyt → relacja 1:N z Wizyta.
# ══════════════════════════════════════════════════════════════════════════════
PLEC_CHOICES = [
    ('M', 'Mężczyzna'),
    ('K', 'Kobieta'),
]

GODZ_PRACY_CHOICES = [
    ('08:00-14:00', '08:00 – 14:00'),
    ('10:00-16:00', '10:00 – 16:00'),
    ('12:00-18:00', '12:00 – 18:00'),
    ('14:00-20:00', '14:00 – 20:00'),
]

DNI_TYGODNIA_CHOICES = [
    ('12345', 'Poniedziałek – Piątek'),
    ('1234',  'Poniedziałek – Czwartek'),
    ('1235',  'Pon, Wt, Śr, Pt'),
    ('246',   'Wtorek, Czwartek, Sobota'),
]


class Lekarz(models.Model):
    # Dane osobowe
    imie = models.CharField(max_length=60, verbose_name='Imię')
    nazwisko = models.CharField(max_length=80, verbose_name='Nazwisko')
    plec = models.CharField(max_length=1, choices=PLEC_CHOICES, default='M', verbose_name='Płeć')
    tytul = models.CharField(
        max_length=20, default='lek. med.',
        verbose_name='Tytuł',
        help_text='Np. dr n. med., lek. med., prof. dr hab.'
    )

    # Relacja z modelem Specjalizacja (ForeignKey = wiele lekarzy do jednej specjalizacji)
    specjalizacja = models.ForeignKey(
        Specjalizacja,
        on_delete=models.PROTECT,       # PROTECT = nie pozwól usunąć specjalizacji jeśli ma lekarzy
        related_name='lekarze',         # umożliwia dostęp: specjalizacja.lekarze.all()
        verbose_name='Specjalizacja'
    )

    # Informacje zawodowe
    doswiadczenie_lat = models.PositiveIntegerField(
        default=5,
        verbose_name='Lata doświadczenia'
    )
    opis = models.TextField(
        verbose_name='O lekarzu',
        help_text='Krótki opis, wykształcenie, metody leczenia'
    )
    ocena = models.DecimalField(
        max_digits=3, decimal_places=1,
        default=4.5,
        verbose_name='Ocena (1–5)'
    )
    liczba_opinii = models.PositiveIntegerField(default=0, verbose_name='Liczba opinii')

    # Dostępność – kiedy pracuje lekarz
    godz_pracy = models.CharField(
        max_length=15,
        choices=GODZ_PRACY_CHOICES,
        default='08:00-14:00',
        verbose_name='Godziny pracy'
    )
    dni_pracy = models.CharField(
        max_length=10,
        choices=DNI_TYGODNIA_CHOICES,
        default='12345',
        verbose_name='Dni tygodnia'
    )
    czas_wizyty_min = models.PositiveIntegerField(
        default=30,
        verbose_name='Czas wizyty (minuty)',
        help_text='Długość jednej wizyty w minutach (15, 20, 30, 45, 60)'
    )

    # Dane kontaktowe / logistyczne
    nr_gabinetu = models.CharField(max_length=10, blank=True, verbose_name='Nr gabinetu')
    miasto = models.CharField(max_length=80, default='Warszawa', verbose_name='Miasto')
    adres = models.CharField(max_length=200, blank=True, verbose_name='Adres placówki')
    cena_wizyty = models.DecimalField(
        max_digits=7, decimal_places=2,
        default=150.00,
        verbose_name='Cena wizyty (zł)'
    )

    aktywny = models.BooleanField(default=True, verbose_name='Profil aktywny')
    data_dodania = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Lekarz'
        verbose_name_plural = 'Lekarze'
        ordering = ['nazwisko', 'imie']

    def __str__(self):
        return f'{self.tytul} {self.imie} {self.nazwisko}'

    @property
    def pelne_imie(self):
        return f'{self.imie} {self.nazwisko}'

    @property
    def tytul_i_nazwisko(self):
        return f'{self.tytul} {self.imie} {self.nazwisko}'

    def dostepne_sloty(self, na_date: date) -> list[time]:
        """
        Zwraca listę dostępnych godzin dla lekarza w podanym dniu.
        Pomija godziny już zarezerwowane przez innych pacjentów.
        """
        # Sprawdź czy ten dzień tygodnia jest dniem pracy (1=Pon, 7=Ndz)
        dzien_tygodnia = str(na_date.isoweekday())
        if dzien_tygodnia not in self.dni_pracy:
            return []

        # Parsuj godziny pracy "08:00-14:00"
        try:
            start_str, end_str = self.godz_pracy.split('-')
            h_start, m_start = map(int, start_str.split(':'))
            h_end, m_end = map(int, end_str.split(':'))
        except (ValueError, AttributeError):
            return []

        start = time(h_start, m_start)
        koniec = time(h_end, m_end)
        krok = self.czas_wizyty_min

        # Wygeneruj wszystkie możliwe sloty
        wszystkie_sloty = []
        aktualny = timedelta(hours=h_start, minutes=m_start)
        koniec_td = timedelta(hours=h_end, minutes=m_end)
        while aktualny < koniec_td:
            h = aktualny.seconds // 3600
            m = (aktualny.seconds % 3600) // 60
            wszystkie_sloty.append(time(h, m))
            aktualny += timedelta(minutes=krok)

        # Pobierz zajęte sloty z bazy
        zarezerwowane = set(
            self.wizyty
            .filter(data=na_date, status__in=['oczekujaca', 'potwierdzona'])
            .values_list('godzina', flat=True)
        )

        return [s for s in wszystkie_sloty if s not in zarezerwowane]


# ══════════════════════════════════════════════════════════════════════════════
# MODEL 3: PACJENT
# Dane pacjenta. Jeden pacjent może mieć wiele wizyt → relacja 1:N z Wizyta.
# ══════════════════════════════════════════════════════════════════════════════
class Pacjent(models.Model):
    imie = models.CharField(max_length=60, verbose_name='Imię')
    nazwisko = models.CharField(max_length=80, verbose_name='Nazwisko')
    email = models.EmailField(verbose_name='Adres e-mail')
    telefon = models.CharField(max_length=15, verbose_name='Numer telefonu')
    data_urodzenia = models.DateField(
        null=True, blank=True,
        verbose_name='Data urodzenia'
    )
    pesel = models.CharField(
        max_length=11, blank=True,
        verbose_name='PESEL',
        help_text='Opcjonalnie'
    )
    data_rejestracji = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Pacjent'
        verbose_name_plural = 'Pacjenci'
        ordering = ['nazwisko', 'imie']

    def __str__(self):
        return f'{self.imie} {self.nazwisko} ({self.email})'


# ══════════════════════════════════════════════════════════════════════════════
# MODEL 4: WIZYTA
# Łączy Lekarza i Pacjenta w konkretnym terminie.
# ForeignKey do Lekarz + ForeignKey do Pacjent = klasyczna relacja wiele-do-wielu
# zrealizowana przez tabelę pośredniczącą (z dodatkowymi polami).
# ══════════════════════════════════════════════════════════════════════════════
STATUS_CHOICES = [
    ('oczekujaca',   'Oczekująca'),
    ('potwierdzona', 'Potwierdzona'),
    ('odbyta',       'Odbyta'),
    ('anulowana',    'Anulowana'),
]


class Wizyta(models.Model):
    # Relacje (ForeignKey)
    lekarz = models.ForeignKey(
        Lekarz,
        on_delete=models.CASCADE,
        related_name='wizyty',   # lekarz.wizyty.all()
        verbose_name='Lekarz'
    )
    pacjent = models.ForeignKey(
        Pacjent,
        on_delete=models.CASCADE,
        related_name='wizyty',   # pacjent.wizyty.all()
        verbose_name='Pacjent'
    )

    # Termin
    data = models.DateField(verbose_name='Data wizyty')
    godzina = models.TimeField(verbose_name='Godzina wizyty')

    # Dodatkowe informacje
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='oczekujaca',
        verbose_name='Status'
    )
    powod_wizyty = models.TextField(
        blank=True,
        verbose_name='Powód wizyty / objawy',
        help_text='Opcjonalny opis problemu'
    )
    notatki_lekarza = models.TextField(
        blank=True,
        verbose_name='Notatki lekarza (widoczne tylko dla personelu)'
    )
    data_rezerwacji = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data dokonania rezerwacji'
    )

    class Meta:
        verbose_name = 'Wizyta'
        verbose_name_plural = 'Wizyty'
        ordering = ['data', 'godzina']
        # Jeden lekarz nie może mieć dwóch wizyt w tym samym terminie
        unique_together = [('lekarz', 'data', 'godzina')]

    def __str__(self):
        return (
            f'{self.lekarz.nazwisko} | {self.pacjent.imie} {self.pacjent.nazwisko} | '
            f'{self.data.strftime("%d.%m.%Y")} {self.godzina.strftime("%H:%M")}'
        )

    @property
    def czy_przyszla(self):
        return self.data >= date.today()

    @property
    def status_badge_kolor(self):
        """Zwraca klasę Bootstrap dla koloru badge statusu."""
        return {
            'oczekujaca':   'warning',
            'potwierdzona': 'success',
            'odbyta':       'secondary',
            'anulowana':    'danger',
        }.get(self.status, 'light')
