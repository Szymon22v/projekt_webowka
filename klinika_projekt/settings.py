"""
Ustawienia Django dla projektu KlinikaApp.
"""
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# Klucz sekretny – zmień go przed wdrożeniem na serwer!
SECRET_KEY = 'django-insecure-klinika-projekt-klucz-zmien-na-produkcji-2024'

# W trybie produkcyjnym ustaw na False i skonfiguruj ALLOWED_HOSTS
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Nasza aplikacja:
    'wizytownik',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'klinika_projekt.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Folder z szablonami HTML:
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'klinika_projekt.wsgi.application'

# Baza danych – SQLite (plik lokalny, nie wymaga instalacji serwera)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Walidacja haseł
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'pl'
TIME_ZONE = 'Europe/Warsaw'
USE_I18N = True
USE_TZ = True

# ─── Pliki statyczne (CSS, JS, Bootstrap, FontAwesome) ────────────────────────
# Serwowane z naszego serwera zgodnie z wymogiem punktu 2
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']   # folder deweloperski
STATIC_ROOT = BASE_DIR / 'staticfiles'     # folder produkcyjny (po collectstatic)

# ─── Pliki mediów (zdjęcia lekarzy) ───────────────────────────────────────────
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Liczba wizyt na stronie (paginacja – punkt 5)
WIZYTY_NA_STRONE = 10
LEKARZE_NA_STRONE = 9
