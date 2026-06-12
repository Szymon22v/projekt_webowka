from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-klinika-projekt-klucz-zmien-na-produkcji-2024'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
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
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'wizytownik.context_processors.admin_status',
            ],
        },
    },
]

WSGI_APPLICATION = 'klinika_projekt.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

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

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─── Logowanie / Autoryzacja ──────────────────────────────────────────────────
LOGIN_URL = '/logowanie/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# ─── LISTA ADMINÓW ────────────────────────────────────────────────────────────
# Aby nadać komuś dostęp do Panelu – dopisz nazwę użytkownika do listy.
# Aby zabrać dostęp – usuń nazwę z listy.
ADMINZY = [
    'admin',
]

# ═══════════════════════════════════════════════════════════════════════════════
# KONFIGURACJA E-MAIL
# ═══════════════════════════════════════════════════════════════════════════════

# ── OPCJA A: Terminal (domyślnie włączona) ────────────────────────────────────
# Maile NIE są wysyłane – wyświetlają się w terminalu gdzie działa serwer.
# Idealne do testowania i na obronę projektu. Zero konfiguracji.

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# ── OPCJA B: Prawdziwy Gmail ──────────────────────────────────────────────────
# Aby wysyłać prawdziwe maile przez Gmail:
#
# 1. Wejdź na https://myaccount.google.com
# 2. Bezpieczeństwo → Weryfikacja dwuetapowa → włącz (jeśli nie włączona)
# 3. Bezpieczeństwo → Hasła aplikacji → wybierz "Poczta" → kopiuj 16-znakowe hasło
# 4. Odkomentuj poniższy blok (usuń #) i wpisz swoje dane:
#
# EMAIL_BACKEND   = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST      = 'smtp.gmail.com'
# EMAIL_PORT      = 587
# EMAIL_USE_TLS   = True
# EMAIL_HOST_USER = 'twoj.adres@gmail.com'       # ← wpisz swój Gmail
# EMAIL_HOST_PASSWORD = 'xxxx xxxx xxxx xxxx'    # ← wklej hasło aplikacji z Google
# DEFAULT_FROM_EMAIL  = 'KlinikaApp <twoj.adres@gmail.com>'
#
# PAMIĘTAJ: po zmianie na Gmail zakomentuj linię EMAIL_BACKEND powyżej (Opcja A)!
