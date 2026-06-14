# 🏥 KlinikaApp – Portal Rezerwacji Wizyt Lekarskich

Projekt zaliczeniowy z przedmiotu **Programowanie Aplikacji Webowych**.  
Aplikacja wzorowana na portalu „Znany Lekarz" – pacjent może przejrzeć lekarzy specjalistów, wybrać termin i zarezerwować wizytę online.

---

## 🚀 Uruchomienie projektu

### Krok 1 – Utwórz wirtualne środowisko
```bash
python -m venv venv
```

### Krok 2 – Aktywuj środowisko
```bash
# Windows:
venv\Scripts\activate

# Mac / Linux:
source venv/bin/activate
```

### Krok 3 – Zainstaluj wymagane biblioteki
```bash
pip install -r requirements.txt
```

### Krok 4 – Zainicjalizuj bazę danych
```bash
python manage.py makemigrations
python manage.py migrate
```

### Krok 5 – Załaduj przykładowe dane
```bash
python manage.py zaladuj_dane
```

### Krok 6 – Utwórz konta użytkowników
```bash
python manage.py stworz_uzytkownikow
```

### Krok 7 – Uruchom serwer
```bash
python manage.py runserver
```

Otwórz przeglądarkę i wejdź na: **http://127.0.0.1:8000**

---

## 🔐 Konta testowe

| Rola | Login | Hasło |
|------|-------|-------|
| Administrator | `admin` | `Admin1234!` |
| Użytkownik | `jan_kowalski` | `Haslo1234!` |
| Użytkownik | `anna_nowak` | `Haslo1234!` |
| Użytkownik | `piotr_wisniewski` | `Haslo1234!` |
| Użytkownik | `maria_dabrowska` | `Haslo1234!` |
| Użytkownik | `tomasz_lewandowski` | `Haslo1234!` |

---

## 📋 Adresy URL

| Adres | Opis |
|-------|------|
| `/` | Strona główna – wyszukiwarka lekarzy |
| `/lekarze/` | Lista lekarzy z filtrowaniem |
| `/lekarze/<id>/` | Profil lekarza + wybór terminu |
| `/rezerwacja/<id>/` | Formularz rezerwacji wizyty |
| `/wizyty/moje/` | Moje wizyty (wyszukaj po e-mailu) |
| `/logowanie/` | Strona logowania |
| `/panel/` | Panel zarządzania (tylko admin) |
| `/panel/wizyty/` | Lista wszystkich wizyt |
| `/eksport/` | Eksport danych CSV / XLSX / PNG |
| `/eksport/statystyki/` | Statystyki z wykresami |
| `/import/` | Import danych z pliku CSV |

---

## 📁 Struktura projektu

```
projekt_webowka/
├── klinika_projekt/        ← ustawienia Django
│   ├── settings.py         ← konfiguracja (baza, e-mail, lista adminów)
│   └── urls.py             ← główny router URL
├── wizytownik/             ← główna aplikacja
│   ├── models.py           ← modele bazy danych
│   ├── forms.py            ← formularze
│   ├── urls.py             ← adresy URL
│   ├── paginacja.py        ← helper paginacji
│   ├── context_processors.py
│   ├── views/
│   │   ├── publiczne.py    ← widoki dla pacjenta
│   │   ├── zarzadzanie.py  ← panel admina
│   │   ├── eksport.py      ← CSV, XLSX, wykres PNG
│   │   ├── import_plik.py  ← upload pliku CSV
│   │   └── auth_views.py   ← logowanie / wylogowanie
│   └── management/commands/
│       ├── zaladuj_dane.py
│       └── stworz_uzytkownikow.py
├── templates/              ← szablony HTML
├── static/                 ← Bootstrap, Font Awesome, Chart.js, własny CSS/JS
├── manage.py
└── requirements.txt
```

---

## ⚙️ Zmiana uprawnień administratora

Otwórz `klinika_projekt/settings.py` i edytuj listę `ADMINZY`:

```python
ADMINZY = [
    'admin',          # ma dostęp do Panelu
    # 'inny_user',   # odkomentuj aby dodać kolejnego admina
]
```

---

## 📧 Konfiguracja e-mail

Domyślnie powiadomienia po rezerwacji wyświetlają się w terminalu.  
Aby wysyłać prawdziwe maile przez Gmail, odkomentuj blok w `settings.py`:

```python
EMAIL_BACKEND       = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST          = 'smtp.gmail.com'
EMAIL_PORT          = 587
EMAIL_USE_TLS       = True
EMAIL_HOST_USER     = 'twoj.adres@gmail.com'
EMAIL_HOST_PASSWORD = 'xxxx xxxx xxxx xxxx'  # hasło aplikacji Google
```

---

## 🛠️ Przydatne komendy

```bash
# Reset bazy i ponowne załadowanie danych
python manage.py zaladuj_dane --wyczysc

# Panel admina Django (osobny od panelu aplikacji)
python manage.py createsuperuser
# → http://127.0.0.1:8000/admin/
```

---

## 📦 Wymagania

- Python 3.11+
- Django 4.2
- matplotlib 3.7
- openpyxl 3.1
- Pillow 10.0
