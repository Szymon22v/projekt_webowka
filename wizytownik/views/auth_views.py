"""
auth_views.py – Widoki logowania i wylogowania.

Używamy wbudowanego systemu autoryzacji Django (django.contrib.auth).
Nie reinventujemy koła – Django ma gotowe mechanizmy bezpiecznego
przechowywania haseł (bcrypt/PBKDF2) i zarządzania sesją.
"""
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import redirect, render
from django import forms


# ── Formularz logowania ────────────────────────────────────────────────────────
class LoginForm(forms.Form):
    nazwa_uzytkownika = forms.CharField(
        label='Nazwa użytkownika',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Wpisz nazwę użytkownika',
            'autofocus': True,
        })
    )
    haslo = forms.CharField(
        label='Hasło',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Wpisz hasło',
        })
    )


# ── Widok logowania ────────────────────────────────────────────────────────────
def widok_logowania(request):
    """
    GET  – wyświetla formularz logowania
    POST – sprawdza dane i loguje użytkownika
    """
    # Jeśli już zalogowany – przekieruj na stronę główną
    if request.user.is_authenticated:
        return redirect('strona_glowna')

    form = LoginForm()

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            nazwa = form.cleaned_data['nazwa_uzytkownika']
            haslo = form.cleaned_data['haslo']

            # Django sprawdza czy użytkownik istnieje i hasło się zgadza
            user = authenticate(request, username=nazwa, password=haslo)

            if user is not None:
                login(request, user)  # zapisuje sesję w przeglądarce

                # Sprawdź czy admin czy zwykły użytkownik
                from django.conf import settings
                if nazwa in settings.ADMINZY:
                    messages.success(request, f'Zalogowano jako administrator: {nazwa}')
                else:
                    messages.success(request, f'Zalogowano pomyślnie. Witaj, {nazwa}!')

                # Przekieruj tam skąd przyszedł (lub na stronę główną)
                nastepna_strona = request.GET.get('next', '/')
                return redirect(nastepna_strona)
            else:
                messages.error(request, 'Nieprawidłowa nazwa użytkownika lub hasło.')

    return render(request, 'wizytownik/auth/login.html', {'form': form})


# ── Widok wylogowania ──────────────────────────────────────────────────────────
def widok_wylogowania(request):
    """Wylogowuje użytkownika i przekierowuje na stronę główną."""
    nazwa = request.user.username if request.user.is_authenticated else ''
    logout(request)
    if nazwa:
        messages.info(request, f'Wylogowano. Do zobaczenia, {nazwa}!')
    return redirect('strona_glowna')
