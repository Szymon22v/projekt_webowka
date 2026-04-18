"""
forms.py – Formularze Django dla wszystkich modeli.

Formularz Django to klasa, która:
- Definiuje pola do wypełnienia
- Waliduje dane wprowadzone przez użytkownika
- Może automatycznie generować pola na podstawie modelu (ModelForm)
"""
from django import forms
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from .models import Specjalizacja, Lekarz, Pacjent, Wizyta


# ── Klasa bazowa z pomocniczą metodą (unikamy powtarzania kodu) ───────────────
def dodaj_klasy_bootstrap(form):
    """Dodaje klasy Bootstrap do wszystkich pól formularza."""
    for field_name, field in form.fields.items():
        widget = field.widget
        if isinstance(widget, forms.CheckboxInput):
            widget.attrs['class'] = 'form-check-input'
        elif isinstance(widget, forms.Select):
            widget.attrs['class'] = 'form-select'
        elif isinstance(widget, forms.Textarea):
            widget.attrs['class'] = 'form-control'
            widget.attrs.setdefault('rows', 3)
        else:
            widget.attrs['class'] = 'form-control'


# ══════════════════════════════════════════════════════════════════════════════
# FORMULARZ: Specjalizacja
# ══════════════════════════════════════════════════════════════════════════════
class SpecjalizacjaForm(forms.ModelForm):
    class Meta:
        model = Specjalizacja
        fields = ['nazwa', 'opis', 'ikona_fa', 'kolor_karty']
        widgets = {
            'nazwa': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'np. Kardiolog'
            }),
            'opis': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': 'Opis specjalizacji...'
            }),
            'ikona_fa': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'np. fa-heart'
            }),
            'kolor_karty': forms.Select(
                attrs={'class': 'form-select'},
                choices=[
                    ('primary', 'Niebieski (primary)'),
                    ('success', 'Zielony (success)'),
                    ('danger',  'Czerwony (danger)'),
                    ('warning', 'Żółty (warning)'),
                    ('info',    'Jasnoniebieski (info)'),
                    ('dark',    'Ciemny (dark)'),
                ]
            ),
        }


# ══════════════════════════════════════════════════════════════════════════════
# FORMULARZ: Lekarz
# ══════════════════════════════════════════════════════════════════════════════
class LekarzForm(forms.ModelForm):
    class Meta:
        model = Lekarz
        fields = [
            'tytul', 'imie', 'nazwisko', 'plec', 'specjalizacja',
            'doswiadczenie_lat', 'opis', 'ocena', 'liczba_opinii',
            'godz_pracy', 'dni_pracy', 'czas_wizyty_min',
            'nr_gabinetu', 'miasto', 'adres', 'cena_wizyty', 'aktywny'
        ]
        widgets = {
            'tytul': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'np. dr n. med.'
            }),
            'imie': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Imię lekarza'
            }),
            'nazwisko': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nazwisko lekarza'
            }),
            'plec': forms.Select(attrs={'class': 'form-select'}),
            'specjalizacja': forms.Select(attrs={'class': 'form-select'}),
            'doswiadczenie_lat': forms.NumberInput(attrs={
                'class': 'form-control', 'min': 0, 'max': 60
            }),
            'opis': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 4,
                'placeholder': 'Opis lekarza, wykształcenie, specjalizacje...'
            }),
            'ocena': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.1', 'min': '1', 'max': '5'
            }),
            'liczba_opinii': forms.NumberInput(attrs={
                'class': 'form-control', 'min': 0
            }),
            'godz_pracy': forms.Select(attrs={'class': 'form-select'}),
            'dni_pracy': forms.Select(attrs={'class': 'form-select'}),
            'czas_wizyty_min': forms.Select(
                attrs={'class': 'form-select'},
                choices=[(15,'15 min'), (20,'20 min'), (30,'30 min'),
                         (45,'45 min'), (60,'60 min')]
            ),
            'nr_gabinetu': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'np. 203A'
            }),
            'miasto': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Miasto'
            }),
            'adres': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ul. Przykładowa 1, 00-001 Warszawa'
            }),
            'cena_wizyty': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '10', 'min': '0'
            }),
            'aktywny': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_ocena(self):
        ocena = self.cleaned_data.get('ocena')
        if ocena is not None and (ocena < 1 or ocena > 5):
            raise ValidationError('Ocena musi być między 1 a 5.')
        return ocena


# ══════════════════════════════════════════════════════════════════════════════
# FORMULARZ: Pacjent (przy rezerwacji)
# ══════════════════════════════════════════════════════════════════════════════
class PacjentForm(forms.ModelForm):
    class Meta:
        model = Pacjent
        fields = ['imie', 'nazwisko', 'email', 'telefon', 'data_urodzenia', 'pesel']
        widgets = {
            'imie': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Twoje imię'
            }),
            'nazwisko': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Twoje nazwisko'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 'placeholder': 'twoj@email.pl'
            }),
            'telefon': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': '+48 123 456 789'
            }),
            'data_urodzenia': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'},
                format='%Y-%m-%d'
            ),
            'pesel': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Opcjonalnie',
                'maxlength': '11'
            }),
        }


# ══════════════════════════════════════════════════════════════════════════════
# FORMULARZ: Rezerwacja wizyty (wybór daty i godziny)
# ══════════════════════════════════════════════════════════════════════════════
class RezerwacjaForm(forms.Form):
    """
    Formularz pierwszego kroku rezerwacji.
    Pacjent wybiera datę – godziny ładowane są dynamicznie przez JavaScript.
    """
    data = forms.DateField(
        label='Wybierz datę wizyty',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'min': str(date.today() + timedelta(days=1)),
            'max': str(date.today() + timedelta(days=60)),
        }),
        input_formats=['%Y-%m-%d']
    )
    godzina = forms.TimeField(
        label='Godzina',
        widget=forms.HiddenInput(),    # ustawiana przez JavaScript
        input_formats=['%H:%M']
    )
    powod_wizyty = forms.CharField(
        label='Powód wizyty / objawy (opcjonalnie)',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control', 'rows': 3,
            'placeholder': 'Opisz swoje dolegliwości lub powód wizyty...'
        })
    )

    def clean_data(self):
        d = self.cleaned_data.get('data')
        if d and d < date.today() + timedelta(days=1):
            raise ValidationError('Nie można rezerwować wizyt na dzisiaj ani w przeszłości.')
        if d and d > date.today() + timedelta(days=60):
            raise ValidationError('Można rezerwować wizyty maksymalnie 60 dni naprzód.')
        return d


# ══════════════════════════════════════════════════════════════════════════════
# FORMULARZ: Wyszukiwanie lekarzy (z filtrowaniem – punkt 5)
# ══════════════════════════════════════════════════════════════════════════════
class WyszukiwarkaLekarzaForm(forms.Form):
    """
    Formularz wyszukiwania i filtrowania lekarzy.
    Dane przechowywane w pasku adresu (metoda GET).
    """
    szukaj = forms.CharField(
        label='Szukaj',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Imię, nazwisko lub specjalizacja...',
        })
    )
    specjalizacja = forms.ModelChoiceField(
        label='Specjalizacja',
        queryset=Specjalizacja.objects.all(),
        required=False,
        empty_label='Wszystkie specjalizacje',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    miasto = forms.CharField(
        label='Miasto',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'np. Warszawa'
        })
    )
    cena_max = forms.IntegerField(
        label='Cena max (zł)',
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'np. 300'
        })
    )
    ocena_min = forms.DecimalField(
        label='Ocena min',
        required=False,
        min_value=1, max_value=5,
        decimal_places=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'np. 4.0',
            'step': '0.5'
        })
    )


# ══════════════════════════════════════════════════════════════════════════════
# FORMULARZ: Wyszukiwanie własnych wizyt (po emailu)
# ══════════════════════════════════════════════════════════════════════════════
class MojeWizytyForm(forms.Form):
    email = forms.EmailField(
        label='Twój adres e-mail',
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Wpisz e-mail użyty przy rezerwacji'
        })
    )
