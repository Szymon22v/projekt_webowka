from django.db import models
from datetime import date, time, timedelta

PLEC_CHOICES = [('M', 'Mężczyzna'), ('K', 'Kobieta')]
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
STATUS_CHOICES = [
    ('oczekujaca',   'Oczekująca'),
    ('potwierdzona', 'Potwierdzona'),
    ('odbyta',       'Odbyta'),
    ('anulowana',    'Anulowana'),
]


class Specjalizacja(models.Model):
    nazwa       = models.CharField(max_length=100, unique=True, verbose_name='Nazwa')
    opis        = models.TextField(verbose_name='Opis')
    ikona_fa    = models.CharField(max_length=60, default='fa-stethoscope', verbose_name='Ikona FA')
    kolor_karty = models.CharField(max_length=20, default='primary', verbose_name='Kolor Bootstrap')

    class Meta:
        verbose_name = 'Specjalizacja'
        verbose_name_plural = 'Specjalizacje'
        ordering = ['nazwa']

    def __str__(self):
        return self.nazwa


class Lekarz(models.Model):
    imie               = models.CharField(max_length=60, verbose_name='Imię')
    nazwisko           = models.CharField(max_length=80, verbose_name='Nazwisko')
    plec               = models.CharField(max_length=1, choices=PLEC_CHOICES, default='M')
    tytul              = models.CharField(max_length=20, default='lek. med.', verbose_name='Tytuł')
    specjalizacja      = models.ForeignKey(Specjalizacja, on_delete=models.PROTECT,
                                           related_name='lekarze', verbose_name='Specjalizacja')
    doswiadczenie_lat  = models.PositiveIntegerField(default=5, verbose_name='Lata doświadczenia')
    opis               = models.TextField(verbose_name='O lekarzu')
    ocena              = models.DecimalField(max_digits=3, decimal_places=1, default=4.5)
    liczba_opinii      = models.PositiveIntegerField(default=0)
    godz_pracy         = models.CharField(max_length=15, choices=GODZ_PRACY_CHOICES, default='08:00-14:00')
    dni_pracy          = models.CharField(max_length=10, choices=DNI_TYGODNIA_CHOICES, default='12345')
    czas_wizyty_min    = models.PositiveIntegerField(default=30, verbose_name='Czas wizyty (min)')
    nr_gabinetu        = models.CharField(max_length=10, blank=True)
    miasto             = models.CharField(max_length=80, default='Warszawa')
    adres              = models.CharField(max_length=200, blank=True)
    cena_wizyty        = models.DecimalField(max_digits=7, decimal_places=2, default=150.00)
    aktywny            = models.BooleanField(default=True)
    data_dodania       = models.DateTimeField(auto_now_add=True)

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

    def dostepne_sloty(self, na_date):
        dzien = str(na_date.isoweekday())
        if dzien not in self.dni_pracy:
            return []
        try:
            start_str, end_str = self.godz_pracy.split('-')
            h_s, m_s = map(int, start_str.split(':'))
            h_e, m_e = map(int, end_str.split(':'))
        except Exception:
            return []

        sloty = []
        akt = timedelta(hours=h_s, minutes=m_s)
        koniec = timedelta(hours=h_e, minutes=m_e)
        while akt < koniec:
            h = akt.seconds // 3600
            m = (akt.seconds % 3600) // 60
            sloty.append(time(h, m))
            akt += timedelta(minutes=self.czas_wizyty_min)

        zarezerwowane = set(
            self.wizyty.filter(data=na_date, status__in=['oczekujaca', 'potwierdzona'])
            .values_list('godzina', flat=True)
        )
        return [s for s in sloty if s not in zarezerwowane]


class Pacjent(models.Model):
    imie             = models.CharField(max_length=60, verbose_name='Imię')
    nazwisko         = models.CharField(max_length=80, verbose_name='Nazwisko')
    email            = models.EmailField(verbose_name='E-mail')
    telefon          = models.CharField(max_length=15, verbose_name='Telefon')
    data_urodzenia   = models.DateField(null=True, blank=True)
    pesel            = models.CharField(max_length=11, blank=True)
    data_rejestracji = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Pacjent'
        verbose_name_plural = 'Pacjenci'
        ordering = ['nazwisko', 'imie']

    def __str__(self):
        return f'{self.imie} {self.nazwisko} ({self.email})'


class Wizyta(models.Model):
    lekarz         = models.ForeignKey(Lekarz, on_delete=models.CASCADE,
                                       related_name='wizyty', verbose_name='Lekarz')
    pacjent        = models.ForeignKey(Pacjent, on_delete=models.CASCADE,
                                       related_name='wizyty', verbose_name='Pacjent')
    data           = models.DateField(verbose_name='Data wizyty')
    godzina        = models.TimeField(verbose_name='Godzina')
    status         = models.CharField(max_length=15, choices=STATUS_CHOICES, default='oczekujaca')
    powod_wizyty   = models.TextField(blank=True, verbose_name='Powód wizyty')
    notatki_lekarza = models.TextField(blank=True)
    data_rezerwacji = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Wizyta'
        verbose_name_plural = 'Wizyty'
        ordering = ['data', 'godzina']
        unique_together = [('lekarz', 'data', 'godzina')]

    def __str__(self):
        return f'{self.lekarz.nazwisko} | {self.pacjent} | {self.data} {self.godzina}'

    @property
    def czy_przyszla(self):
        return self.data >= date.today()

    @property
    def status_badge_kolor(self):
        return {
            'oczekujaca': 'warning', 'potwierdzona': 'success',
            'odbyta': 'secondary',   'anulowana': 'danger',
        }.get(self.status, 'light')
