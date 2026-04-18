# 🏥 KlinikaApp – Portal Rezerwacji Wizyt Lekarskich

Projekt zaliczeniowy z Programowania Aplikacji Webowych.
Aplikacja wzorowana na portalu „Znany Lekarz" – pacjent może przejrzeć
specjalistów, wybrać lekarza i zarezerwować wolny termin.

---

## 📁 Struktura projektu

```
klinika/
├── klinika_projekt/        ← ustawienia Django (settings, urls)
├── wizytownik/             ← główna aplikacja
│   ├── views/              ← widoki podzielone tematycznie
│   │   ├── publiczne.py    ← strony dla pacjenta
│   │   └── zarzadzanie.py  ← panel administracyjny (dodawanie lekarzy itp.)
│   ├── models.py           ← modele bazy danych
│   ├── forms.py            ← formularze
│   ├── urls.py             ← adresy URL
│   └── management/
│       └── commands/
│           └── zaladuj_dane.py  ← komenda do załadowania przykładowych danych
├── templates/              ← szablony HTML
│   └── wizytownik/
│       ├── lekarze/
│       ├── wizyty/
│       └── zarzadzanie/
├── static/                 ← pliki statyczne (CSS, JS, Bootstrap, FontAwesome)
│   ├── css/
│   ├── js/
│   └── webfonts/
└── fixtures/               ← przykładowe dane JSON
```

---

## 🚀 Instalacja krok po kroku (dla początkujących)

### Krok 1 – Zainstaluj Python
Pobierz Python 3.11+ ze strony https://www.python.org/downloads/
Podczas instalacji zaznacz „Add Python to PATH".

### Krok 2 – Otwórz terminal / wiersz poleceń
- Windows: Szukaj „cmd" lub „PowerShell" w menu Start
- Mac/Linux: Otwórz „Terminal"

Przejdź do folderu projektu:
```
cd ścieżka/do/folderu/klinika
```

### Krok 3 – Utwórz wirtualne środowisko (venv)
Wirtualne środowisko to odizolowana przestrzeń do instalowania bibliotek
tylko dla tego projektu (nie miesza się z resztą systemu).

```bash
python -m venv venv
```

Aktywuj środowisko:
- Windows:  `venv\Scripts\activate`
- Mac/Linux: `source venv/bin/activate`

Po aktywacji zobaczysz `(venv)` na początku linii w terminalu. ✅

### Krok 4 – Zainstaluj wymagane biblioteki
```bash
pip install -r requirements.txt
```

### Krok 5 – Pobierz pliki Bootstrap i Font Awesome (WYMAGANE przez punkt 2)
Pliki bibliotek muszą być serwowane z naszego serwera (nie z CDN).

#### Bootstrap 5
1. Wejdź na: https://getbootstrap.com/docs/5.3/getting-started/download/
2. Kliknij „Download" → pobierz paczkę ZIP
3. Rozpakuj i skopiuj:
   - `bootstrap.min.css` → do folderu `static/css/`
   - `bootstrap.bundle.min.js` → do folderu `static/js/`

#### Font Awesome 6 (Free)
1. Wejdź na: https://fontawesome.com/download
2. Pobierz "Free For Web"
3. Rozpakuj i skopiuj:
   - `css/all.min.css` → do folderu `static/css/`
   - `webfonts/` (cały folder) → do folderu `static/webfonts/`

#### Chart.js
1. Wejdź na: https://www.chartjs.org/docs/latest/getting-started/
2. Pobierz `chart.umd.min.js`
3. Skopiuj do `static/js/`

### Krok 6 – Inicjalizacja bazy danych
```bash
python manage.py makemigrations
python manage.py migrate
```

### Krok 7 – Załaduj przykładowe dane (lekarze, pacjenci, wizyty)
```bash
python manage.py zaladuj_dane
```
To polecenie doda ~10 lekarzy z różnych specjalizacji i przykładowe wizyty.

### Krok 8 – Utwórz konto administratora (opcjonalne)
```bash
python manage.py createsuperuser
```
Podaj nazwę użytkownika, email i hasło.
Panel admina Django dostępny pod: http://127.0.0.1:8000/admin/

### Krok 9 – Uruchom serwer
```bash
python manage.py runserver
```
Otwórz przeglądarkę i wejdź na: **http://127.0.0.1:8000**

---

## 📋 Strony aplikacji

| Adres URL                      | Opis                                          |
|-------------------------------|-----------------------------------------------|
| `/`                           | Strona główna – wyszukiwarka lekarzy          |
| `/lekarze/`                   | Lista wszystkich lekarzy z filtrowaniem       |
| `/lekarze/<id>/`              | Profil lekarza + wybór terminu                |
| `/rezerwacja/<id>/`           | Formularz rezerwacji wizyty                   |
| `/wizyty/moje/`               | Moje wizyty (wyszukaj po e-mailu)             |
| `/panel/`                     | Panel zarządzania (dodawanie lekarzy itp.)    |
| `/panel/dodaj-lekarza/`       | Formularz dodania nowego lekarza              |
| `/panel/wizyty/`              | Lista wszystkich wizyt                        |

---

## 🔧 Przydatne komendy

```bash
# Uruchomienie serwera
python manage.py runserver

# Po każdej zmianie w models.py:
python manage.py makemigrations
python manage.py migrate

# Załadowanie przykładowych danych od nowa:
python manage.py zaladuj_dane --wyczysc
```

---

## 📌 Modele danych

```
Specjalizacja ──< Lekarz ──< Wizyta >── Pacjent
```
- `Specjalizacja` – np. Kardiolog, Dermatolog (1 specjalizacja → wielu lekarzy)
- `Lekarz` – profil lekarza z opisem i dostępnymi godzinami
- `Pacjent` – dane pacjenta
- `Wizyta` – rezerwacja łącząca Lekarza i Pacjenta (data + godzina + status)
