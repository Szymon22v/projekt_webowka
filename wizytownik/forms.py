from django import forms
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from .models import Specjalizacja, Lekarz, Pacjent, Wizyta


class SpecjalizacjaForm(forms.ModelForm):
    class Meta:
        model = Specjalizacja
        fields = ['nazwa', 'opis', 'ikona_fa', 'kolor_karty']
        widgets = {
            'nazwa':       forms.TextInput(attrs={'class': 'form-control'}),
            'opis':        forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'ikona_fa':    forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'np. fa-heart'}),
            'kolor_karty': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('primary','Niebieski'), ('success','Zielony'), ('danger','Czerwony'),
                ('warning','Żółty'), ('info','Jasnoniebieski'), ('dark','Ciemny'),
            ]),
        }


class LekarzForm(forms.ModelForm):
    class Meta:
        model = Lekarz
        fields = ['tytul','imie','nazwisko','plec','specjalizacja','doswiadczenie_lat',
                  'opis','ocena','liczba_opinii','godz_pracy','dni_pracy','czas_wizyty_min',
                  'nr_gabinetu','miasto','adres','cena_wizyty','aktywny']
        widgets = {
            'tytul':             forms.TextInput(attrs={'class': 'form-control'}),
            'imie':              forms.TextInput(attrs={'class': 'form-control'}),
            'nazwisko':          forms.TextInput(attrs={'class': 'form-control'}),
            'plec':              forms.Select(attrs={'class': 'form-select'}),
            'specjalizacja':     forms.Select(attrs={'class': 'form-select'}),
            'doswiadczenie_lat': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'opis':              forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'ocena':             forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '1', 'max': '5'}),
            'liczba_opinii':     forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'godz_pracy':        forms.Select(attrs={'class': 'form-select'}),
            'dni_pracy':         forms.Select(attrs={'class': 'form-select'}),
            'czas_wizyty_min':   forms.Select(attrs={'class': 'form-select'},
                                              choices=[(15,'15 min'),(20,'20 min'),(30,'30 min'),(45,'45 min'),(60,'60 min')]),
            'nr_gabinetu':       forms.TextInput(attrs={'class': 'form-control'}),
            'miasto':            forms.TextInput(attrs={'class': 'form-control'}),
            'adres':             forms.TextInput(attrs={'class': 'form-control'}),
            'cena_wizyty':       forms.NumberInput(attrs={'class': 'form-control', 'step': '10'}),
            'aktywny':           forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_ocena(self):
        ocena = self.cleaned_data.get('ocena')
        if ocena is not None and (ocena < 1 or ocena > 5):
            raise ValidationError('Ocena musi być między 1 a 5.')
        return ocena


class PacjentForm(forms.ModelForm):
    class Meta:
        model = Pacjent
        fields = ['imie','nazwisko','email','telefon','data_urodzenia','pesel']
        widgets = {
            'imie':           forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Imię'}),
            'nazwisko':       forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nazwisko'}),
            'email':          forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'adres@email.pl'}),
            'telefon':        forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+48 123 456 789'}),
            'data_urodzenia': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'pesel':          forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opcjonalnie', 'maxlength': '11'}),
        }


class RezerwacjaForm(forms.Form):
    data = forms.DateField(
        label='Wybierz datę',
        widget=forms.DateInput(attrs={
            'class': 'form-control', 'type': 'date',
            'min': str(date.today() + timedelta(days=1)),
            'max': str(date.today() + timedelta(days=60)),
        }),
        input_formats=['%Y-%m-%d']
    )
    godzina = forms.TimeField(
        widget=forms.HiddenInput(),
        input_formats=['%H:%M']
    )

    def clean_data(self):
        d = self.cleaned_data.get('data')
        if d and d < date.today() + timedelta(days=1):
            raise ValidationError('Nie można rezerwować na dziś ani w przeszłości.')
        return d


class WyszukiwarkaLekarzaForm(forms.Form):
    szukaj = forms.CharField(
        label='Szukaj', required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Imię, nazwisko, specjalizacja...'})
    )
    specjalizacja = forms.ModelChoiceField(
        label='Specjalizacja', queryset=Specjalizacja.objects.all(),
        required=False, empty_label='Wszystkie specjalizacje',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    miasto = forms.CharField(
        label='Miasto', required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'np. Warszawa'})
    )
    cena_max = forms.IntegerField(
        label='Cena max (zł)', required=False, min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'np. 300'})
    )
    ocena_min = forms.DecimalField(
        label='Ocena min', required=False,
        min_value=1, max_value=5, decimal_places=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'np. 4.0', 'step': '0.5'})
    )


class MojeWizytyForm(forms.Form):
    email = forms.EmailField(
        label='Twój adres e-mail',
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Wpisz e-mail użyty przy rezerwacji'
        })
    )


class ImportPlikuForm(forms.Form):
    TYP_CHOICES = [('pacjenci', 'Pacjenci'), ('lekarze', 'Lekarze')]
    plik = forms.FileField(
        label='Wybierz plik CSV lub TXT',
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.csv,.txt'}),
        help_text='Dozwolone: .csv, .txt | Maks. 5 MB | Separator: średnik (;)'
    )
    typ_danych = forms.ChoiceField(
        choices=TYP_CHOICES, label='Rodzaj danych',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    separator = forms.ChoiceField(
        choices=[(';', 'Średnik (;)'), (',', 'Przecinek (,)'), ('\t', 'Tabulator')],
        label='Separator', initial=';',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    tylko_podglad = forms.BooleanField(
        required=False, label='Tylko podgląd (nie zapisuj do bazy)', initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def clean_plik(self):
        plik = self.cleaned_data.get('plik')
        if plik:
            if not plik.name.lower().endswith(('.csv', '.txt')):
                raise forms.ValidationError('Dozwolone są tylko pliki .csv i .txt')
            if plik.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Plik jest zbyt duży. Maks. 5 MB')
        return plik
