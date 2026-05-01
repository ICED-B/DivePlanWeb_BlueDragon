# Autentizacni service, registrace, prihlaseni, zmena hesla, odhlaseni a rotace tokenu
# validace vstupu a prace s hesly probiha zde
from __future__ import annotations

from typing import Dict, Tuple
from sqlalchemy import or_

from app.db import db
from app.models.app_user import AppUser
from app.utils.password import (
    hash_password,
    verify_password,
    validate_password_strength,
)
from app.utils.jwt import (
    issue_tokens_for_user,
    rotate_refresh_token,
    revoke_current_token,
)
from app.services.audit_events import audit_login, audit_register, audit_change_password


class AuthServiceError(Exception):
    """Chyba autentizace/registrace, routy prevadi na HTTP 400/401"""


def register_user(
    *,
    login: str,
    heslo: str,
    first_name: str | None = None,
    last_name: str | None = None,
    phone: str | None = None,
    email: str | None = None,
) -> Dict[str, str]:

    # Zaregistruje noveho uzivatele a ulozi jej do DB (AuthServiceError pro duplicitni login, email a slabe heslo)
    login = (login or "").strip()
    email = (email or "").lower().strip() or None
    first_name = (first_name or "").strip() or None
    last_name = (last_name or "").strip() or None
    phone = (phone or "").strip() or None

    # Povinne: login + heslo (email je volitelny)
    if not login or not heslo:
        raise AuthServiceError("Chybi povinne udaje.")

    # Kontrola duplicitniho loginu (vzdy)
    q = db.session.query(AppUser.user_id).filter(AppUser.login == login)

    # Email kontroluj jen pokud je vyplneny
    if email:
        q = q.union(
            db.session.query(AppUser.user_id).filter(AppUser.email == email)
        )

    exists = q.first()
    if exists:
        raise AuthServiceError(
            "Uzivatel s timto loginem nebo e-mailem jiz existuje.")

    ok, msg = validate_password_strength(heslo)
    if not ok:
        raise AuthServiceError(msg)

    user = AppUser(
        login=login,
        email=email,
        phone=phone,
        first_name=first_name,
        last_name=last_name,
        password_hash=hash_password(heslo),
        role="user",        # vždy user pri registraci
        is_active=True,     # aktivni pri vytvoreni
    )

    db.session.add(user)
    try:
        db.session.commit()
        audit_register(user_id=user.user_id,
                       login=user.login, email=user.email)
    except Exception:
        db.session.rollback()
        raise AuthServiceError("Registrace selhala.")

    # Vygeneruj cerstve tokeny ihned po registraci (fresh=True)
    tokens = issue_tokens_for_user(user.user_id, fresh=True)
    return {"message": "Registrace uspesna.", **tokens}


def authenticate_user(login_or_email: str, heslo: str) -> Dict[str, str]:
    # Prihlaseni pres login nebo email, vraci zpravu spolu access a refresh tok
    ident = (login_or_email or "").strip()
    if not ident or not heslo:
        raise AuthServiceError("Chybi login/e-mail nebo heslo.")

    # E-mail porovnavame case-insensitive pres lower()
    ident_email = ident.lower()

    user = (
        db.session.query(AppUser)
        .filter(or_(AppUser.login == ident, AppUser.email == ident_email))
        .first()
    )

    if not user:
        raise AuthServiceError("Neplatny login/e-mail nebo heslo.")

    # Deaktivovany ucet odmitne prihlaseni
    if getattr(user, "is_active", True) is False:
        raise AuthServiceError("Ucet je deaktivovany.")

    if not verify_password(heslo, user.password_hash):
        raise AuthServiceError("Neplatny login/e-mail nebo heslo.")

    audit_login(user_id=user.user_id)
    tokens = issue_tokens_for_user(user.user_id, fresh=True)
    return {"message": "Prihlaseni uspesne.", **tokens}


def change_password(user_id: int, stare_heslo: str, nove_heslo: str) -> str:
    # zmena hesla uzivatele (po uspesne zmene revokuje access token)
    user = db.session.get(AppUser, user_id)
    if not user:
        raise AuthServiceError("Uzivatel nenalezen.")

    if not verify_password(stare_heslo, user.password_hash):
        raise AuthServiceError("Stare heslo nesouhlasi.")

    ok, msg = validate_password_strength(nove_heslo)
    if not ok:
        raise AuthServiceError(msg)

    user.password_hash = hash_password(nove_heslo)
    try:
        db.session.commit()
        audit_change_password(user_id=user.user_id)
    except Exception:
        db.session.rollback()
        raise AuthServiceError("Zmena hesla selhala.")

    # Bezpecnostni opatreni -- zneplatni aktualni access token
    revoke_current_token()
    return "Heslo zmeneno. Pris e znovu."


def refresh_tokens(refresh_jwt: dict) -> Tuple[str, str]:
    # Rotace refresh tokenu vraci (access, refresh), stary je revokovan
    return rotate_refresh_token(refresh_jwt)


def logout_current() -> None:    # revokace aktualniho JWT pri odhlaseni
    revoke_current_token()


def get_me_payload(user_id: int) -> Dict[str, object]:
    # Vraci data prihlaseneho uzivatele
    user = db.session.get(AppUser, user_id)
    if not user:
        raise AuthServiceError("Uzivatel nenalezen.")

    return {
        "login": user.login,
        "email": user.email,
        "phone": user.phone,
        "is_active": bool(getattr(user, "is_active", True)),
        "created_at": user.created_at,
        "updated_at": user.updated_at,
    }
