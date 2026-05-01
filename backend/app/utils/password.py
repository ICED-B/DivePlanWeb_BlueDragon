# hashovani a validace hesel
# pouziva bcrypt (passlib) a pri nedostupnosti prechazi na PBKDF2 (werkzeug)
import re
from typing import Tuple

from werkzeug.security import generate_password_hash, check_password_hash

_HAS_PASSLIB = False
bcrypt = None

try:
    from passlib.hash import bcrypt as _bcrypt  # type: ignore
    bcrypt = _bcrypt
    _HAS_PASSLIB = True
except Exception:
    _HAS_PASSLIB = False
    bcrypt = None


def _pbkdf2_hash(plain: str) -> str:
    # Vytvori PBKDF2 SHA256 hash hesla pres wekzeug
    return generate_password_hash(plain, method="pbkdf2:sha256", salt_length=16)


def hash_password(plain: str) -> str:
    # vraci hash hesla preferuje bcrypt
    # werkzeug pokud passlib neni dostupna nebo selze z jineho duvodu

    if _HAS_PASSLIB and bcrypt is not None:
        try:
            # bcrypt ma limit 72 bajtu v UTF-8 delsi hesla hasujeme PBKDF2
            if len(plain.encode("utf-8")) > 72:
                return _pbkdf2_hash(plain)
            return bcrypt.using(rounds=12).hash(plain)
        except Exception:
            # Kdykoli se passlib/bcrypt rozbije, neshodime registraci
            return _pbkdf2_hash(plain)

    return _pbkdf2_hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    # zadane hesla overuje proti ulozenemu hashi (rozlisuje bcrupt a PBKDF2)
    # bcrypt hash typicky zacina $2a$ nebo $2b$ (Flase pri chybe)
    if _HAS_PASSLIB and bcrypt is not None and isinstance(hashed, str) and hashed.startswith("$2"):
        try:
            # Hesla delsi nez 72 bajtu okamzite zamitame
            if len(plain.encode("utf-8")) > 72:
                return False
            return bcrypt.verify(plain, hashed)
        except Exception:
            return False

    # werkzeug PBKDF2 fallback
    try:
        return check_password_hash(hashed, plain)
    except Exception:
        return False


# Validace sily hesla (min. 12 znaku, 1 cislice, 1 special, 1 male, 1 velke pismeno)
_MIN_LEN = 12
_RX_DIGIT = re.compile(r"\d")
_RX_LOWER = re.compile(r"[a-z]")
_RX_UPPER = re.compile(r"[A-Z]")
_RX_SPEC = re.compile(r"[^\w\s]")


def validate_password_strength(pwd: str) -> Tuple[bool, str]:
    # overuje silu hesla dle nastavenych pravidel (pripadne rika chybove hlasky)
    if not pwd or len(pwd) < _MIN_LEN:
        return False, f"Heslo musí mít alespoň {_MIN_LEN} znaků."
    if not _RX_DIGIT.search(pwd):
        return False, "Heslo musí obsahovat alespoň 1 číslici."
    if not _RX_LOWER.search(pwd):
        return False, "Heslo musí obsahovat alespoň 1 malé písmeno."
    if not _RX_UPPER.search(pwd):
        return False, "Heslo musí obsahovat alespoň 1 velké písmeno."
    if not _RX_SPEC.search(pwd):
        return False, "Heslo musí obsahovat alespoň 1 speciální znak."
    return True, "OK"
