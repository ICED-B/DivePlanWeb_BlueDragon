# preklad bez externich zavislosti
from __future__ import annotations

import contextlib
from typing import Dict

_SUPPORTED_LOCALES = {"en", "cs"}
_current_locale = "cs"  # vychozi jazyk

# klice jsou teckami oddelene cesty, hodnoty jsou preklady dle jazyku
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # Obecne
    "ok": {"cs": "OK", "en": "OK"},
    "error.unknown": {"cs": "Neznámá chyba.", "en": "Unknown error."},
    "error.validation": {
        "cs": "Neplatná hodnota pro '{field}'.",
        "en": "Invalid value for '{field}'.",
    },
    "error.unauthorized": {"cs": "Neautorizováno.", "en": "Unauthorized."},
    "error.forbidden": {"cs": "Přístup odepřen.", "en": "Forbidden."},
    "error.not_found": {"cs": "Nenalezeno.", "en": "Not found."},

    # Auth
    "auth.register.success": {"cs": "Registrace úspěšná.", "en": "Registration successful."},
    "auth.login.success": {"cs": "Přihlášení úspěšné.", "en": "Login successful."},
    "auth.logout.success": {"cs": "Byl jsi odhlášen.", "en": "You have been logged out."},
    "auth.password.changed": {"cs": "Heslo změněno. Přihlas se znovu.", "en": "Password changed. Please log in again."},
    "auth.bad_credentials": {"cs": "Neplatný login nebo heslo.", "en": "Invalid login or password."},
    "auth.user_exists": {"cs": "Uživatel již existuje.", "en": "User already exists."},

    # Ponory / Data
    "dive.saved": {"cs": "Ponor uložen.", "en": "Dive saved."},
    "dive.deleted": {"cs": "Ponor smazán.", "en": "Dive deleted."},
    "dive.updated": {"cs": "Ponor upraven.", "en": "Dive updated."},

    # Rate limit
    "rate.limit.exceeded": {"cs": "Příliš mnoho požadavků.", "en": "Too many requests."},

    # Jednotky - labely pro UI
    "unit.m": {"cs": "m", "en": "m"},
    "unit.ft": {"cs": "ft", "en": "ft"},
    "unit.bar": {"cs": "bar", "en": "bar"},
    "unit.psi": {"cs": "psi", "en": "psi"},
    "unit.l": {"cs": "l", "en": "l"},
    "unit.cuft": {"cs": "cu ft", "en": "cu ft"},
    "unit.c": {"cs": "°C", "en": "°C"},
    "unit.f": {"cs": "°F", "en": "°F"},
    "unit.kg": {"cs": "kg", "en": "kg"},
    "unit.lb": {"cs": "lb", "en": "lb"},
    "unit.min": {"cs": "min", "en": "min"},
    "unit.s": {"cs": "s", "en": "s"},
}


def set_locale(locale: str) -> None:    # nastavi aktualni jazyk, ignorovany jsou nepodporovane
    global _current_locale
    if locale in _SUPPORTED_LOCALES:
        _current_locale = locale


def get_locale() -> str:    # vraci jazyk aktualni
    return _current_locale


@contextlib.contextmanager
def with_locale(locale: str):   # pro docasne prepnuti jazyka uvnitr
    old = get_locale()
    try:
        set_locale(locale)
        yield
    finally:
        # Obnovi puvodni jazyk i v pripade vyjimky
        set_locale(old)


def translate(key: str, **params) -> str:
    # vraci retezec pro dany klic v danem jazyce (pokud neexistuje vraci samotny klic)
    lang = get_locale()
    bundle = TRANSLATIONS.get(key)
    if not bundle:
        return key
    # Fallback na anglicke zneni, kdyz pro aktualni jazyk preklad chybi
    template = bundle.get(lang) or bundle.get("en") or key
    try:
        return template.format(**params) if params else template
    except Exception:
        # Kdyz chybi nektery parametr, vrát klic misto vyjimky
        return key

# Alias pro kratsi zapis v aplikacnim kodu
_ = translate
