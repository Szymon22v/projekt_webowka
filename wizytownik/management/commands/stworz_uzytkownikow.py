"""
stworz_uzytkownikow.py – Komenda Django tworząca konta użytkowników.

Użycie:
    python manage.py stworz_uzytkownikow

Tworzy:
    - 1 konto administratora (nazwa w settings.ADMINZY)
    - 5 zwykłych kont użytkowników

Aby zmienić kto jest adminem – edytuj settings.py (lista ADMINZY).
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings


class Command(BaseCommand):
    help = 'Tworzy przykładowe konta użytkowników (1 admin + 5 zwykłych)'

    def handle(self, *args, **options):
        self.stdout.write('\n👤 Tworzę konta użytkowników...\n')

        # ── Konto administratora ──────────────────────────────────────────
        # Nazwa admina pochodzi z settings.ADMINZY (pierwsza na liście)
        admin_nazwa = settings.ADMINZY[0] if settings.ADMINZY else 'admin'

        if User.objects.filter(username=admin_nazwa).exists():
            self.stdout.write(f'   ⚠️  Admin „{admin_nazwa}" już istnieje – pomijam.')
        else:
            User.objects.create_user(
                username=admin_nazwa,
                password='Admin1234!',
                email='admin@klinika.pl',
                first_name='Administrator',
                last_name='Systemu',
                is_staff=True,      # dostęp do /admin/ Django
            )
            self.stdout.write(
                self.style.SUCCESS(f'   ✅ Admin „{admin_nazwa}" utworzony.')
            )

        # ── Zwykłe konta użytkowników ─────────────────────────────────────
        # Typ: 'zwykly' – BRAK dostępu do panelu zarządzania
        zwykli = [
            ('jan_kowalski',       'Jan',     'Kowalski',     'jan@example.pl'),
            ('anna_nowak',         'Anna',    'Nowak',        'anna@example.pl'),
            ('piotr_wisniewski',   'Piotr',   'Wiśniewski',   'piotr@example.pl'),
            ('maria_dabrowska',    'Maria',   'Dąbrowska',    'maria@example.pl'),
            ('tomasz_lewandowski', 'Tomasz',  'Lewandowski',  'tomasz@example.pl'),
        ]

        for nazwa, imie, nazwisko, email in zwykli:
            if User.objects.filter(username=nazwa).exists():
                self.stdout.write(f'   ⚠️  Użytkownik „{nazwa}" już istnieje – pomijam.')
            else:
                User.objects.create_user(
                    username=nazwa,
                    password='Haslo1234!',
                    email=email,
                    first_name=imie,
                    last_name=nazwisko,
                    is_staff=False,     # brak dostępu do /admin/
                )
                self.stdout.write(
                    self.style.SUCCESS(f'   ✅ Użytkownik „{nazwa}" utworzony.')
                )

        # ── Podsumowanie ──────────────────────────────────────────────────
        self.stdout.write(self.style.SUCCESS(
            f'\n🎉 Gotowe! Konta użytkowników:\n'
            f'\n'
            f'   ADMINISTRATOR (dostęp do Panelu):\n'
            f'   ┌─────────────────────────────────────┐\n'
            f'   │ Login:  {admin_nazwa:<28} │\n'
            f'   │ Hasło:  Admin1234!                  │\n'
            f'   └─────────────────────────────────────┘\n'
            f'\n'
            f'   ZWYKLI UŻYTKOWNICY (brak dostępu do Panelu):\n'
            f'   Login: jan_kowalski / anna_nowak /\n'
            f'          piotr_wisniewski / maria_dabrowska /\n'
            f'          tomasz_lewandowski\n'
            f'   Hasło: Haslo1234! (dla wszystkich)\n'
            f'\n'
            f'   ℹ️  Aby zmienić kto jest adminem:\n'
            f'      Edytuj listę ADMINZY w pliku klinika_projekt/settings.py\n'
        ))
