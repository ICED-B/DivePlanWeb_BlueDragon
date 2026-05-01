# Funkce pro praci s JWT tokeny
# zajistuje obnovu refresh tokenu pres blacklist
from typing import Tuple, Dict, Any
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt,
    get_jwt_identity,
)

from ..extensions import db
from ..models.token_blacklist import TokenBlacklist


def issue_tokens_for_user(user_id: int, fresh: bool = True) -> Dict[str, str]:
    # vyda access spolu s refresh tokenem  
    # (Parametry jsou user_id a fresh kdy Treu pri prihlaseni a False pri rotaci)
    # JWT identity musi byt string
    identity = str(user_id)
    access_token = create_access_token(identity=identity, fresh=fresh)
    refresh_token = create_refresh_token(identity=identity)
    return {"access_token": access_token, "refresh_token": refresh_token}


def rotate_refresh_token(old_refresh_jwt: dict) -> Tuple[str, str]:
    # Obnova refresh tokenu zneplatni stary a vyda novy par (JTI do blacklistu)
    # vraci (access_token a refresh_token) kdy fresh pouze pri prihlaseni
    jti = old_refresh_jwt.get("jti")
    identity = old_refresh_jwt.get("sub")  # bude string
    if jti:
        _blacklist_jti(jti)
    access = create_access_token(identity=identity, fresh=False)
    refresh = create_refresh_token(identity=identity)
    return access, refresh


def revoke_current_token() -> None:     # znaplatni aktualni JWT pridanim JTI do blacklistu
    payload = get_jwt()
    jti = payload.get("jti")
    if jti:
        _blacklist_jti(jti)


def _blacklist_jti(jti: str) -> None:   # JTI do TokenBlacklist (pri chybe DB rollback)
    try:
        db.session.add(TokenBlacklist(jti=jti))
        db.session.commit()
    except Exception:
        db.session.rollback()


def get_identity() -> int:
    raw = get_jwt_identity()
    try:
        return int(raw)
    except Exception:
        return 0
