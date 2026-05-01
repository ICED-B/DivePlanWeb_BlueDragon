# Funkce pro zapis audit logu spojene s uzivatelem
# volani write_audit s pred definovanou akci a entitou
from __future__ import annotations
from typing import Optional, Dict, Any

from app.services.audit_log_service import write_audit

# Nazev entity v audit logu pro uzivatelsky ucet
ENTITY_USER = "AppUser"


def audit_register(*, user_id: int, login: str, email: str | None) -> None:     # Zaznam registrace
    write_audit(
        user_id=user_id,
        performed_by=user_id,
        action="REGISTER",
        entity=ENTITY_USER,
        entity_id=str(user_id),
        changes={"login": login, "email": email},
    )


def audit_login(*, user_id: int) -> None:   # Zaznam loginu
    write_audit(
        user_id=user_id,
        performed_by=user_id,
        action="LOGIN",
        entity=ENTITY_USER,
        entity_id=str(user_id),
    )


def audit_logout(*, user_id: int) -> None:  # Zaznam odhlaseni (revokace)
    write_audit(
        user_id=user_id,
        performed_by=user_id,
        action="LOGOUT",
        entity=ENTITY_USER,
        entity_id=str(user_id),
    )


def audit_change_password(*, user_id: int) -> None:     # Zaznam o zmene hesla (bez zaznamenani hesla)
    write_audit(
        user_id=user_id,
        performed_by=user_id,
        action="CHANGE_PASSWORD",
        entity=ENTITY_USER,
        entity_id=str(user_id),
    )


def audit_profile_update(*, user_id: int, before: Dict[str, Any], after: Dict[str, Any]) -> None:   # Zaznam zmeny v profilu 
    write_audit(
        user_id=user_id,
        performed_by=user_id,
        action="UPDATE_PROFILE",
        entity=ENTITY_USER,
        entity_id=str(user_id),
        changes={"before": before, "after": after},
    )


def audit_delete_account(*, user_id: int) -> None:      # Zaznam o deletu profilu
    write_audit(
        user_id=user_id,
        performed_by=user_id,
        action="DELETE_ACCOUNT",
        entity=ENTITY_USER,
        entity_id=str(user_id),
    )
