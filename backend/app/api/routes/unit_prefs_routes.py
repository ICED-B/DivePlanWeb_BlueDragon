# sprava preferenci uzivatele (jednotky)
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt

from app.schemas import UnitPrefsSchema, UnitPrefsUpdateSchema
from app.utils.jwt import get_identity
from app.services.unit_prefs_service import (
    get_prefs_for_user,
    set_prefs_for_user,
    prefs_from_dict,
)

blp = Blueprint(
    "unit_prefs",
    __name__,
    url_prefix="/api/v1/unit-prefs",
    description="Unit preferences stored per AppUser.user_id",
)


def _is_admin() -> bool:
    claims = get_jwt()
    return (claims.get("role") or "").lower() == "admin"


def _prefs_to_response(user_id: int, prefs_obj) -> dict:
    # prevede dataclass UnitPrefs na slovnik pro JSON odpoved
    return {"user_id": user_id, **{k: v.value for k, v in prefs_obj.__dict__.items()}}


@blp.route("/me", methods=["GET"])
@jwt_required()
@blp.response(200, UnitPrefsSchema)
def get_my_unit_prefs():
    user_id = get_identity()
    prefs = get_prefs_for_user(user_id)
    return _prefs_to_response(user_id, prefs)


@blp.route("/me", methods=["PATCH"])
@jwt_required()
@blp.arguments(UnitPrefsUpdateSchema)
@blp.response(200, UnitPrefsSchema)
def update_my_unit_prefs(payload: dict):
    user_id = get_identity()

    # Nacist aktualni stav, soucasne pouzivane hodnoty prevest na retezce
    current = get_prefs_for_user(user_id)
    merged_dict = {**{k: v.value for k, v in current.__dict__.items()}, **(payload or {})}
    merged = prefs_from_dict(merged_dict)

    saved = set_prefs_for_user(user_id, merged)
    return _prefs_to_response(user_id, saved)



@blp.route("/<int:user_id>", methods=["GET"])
@jwt_required()
@blp.response(200, UnitPrefsSchema)
def get_unit_prefs_for_user(user_id: int):
    if not _is_admin():
        abort(403, message="Only admin can view other users' unit prefs.")
    prefs = get_prefs_for_user(user_id)
    return _prefs_to_response(user_id, prefs)


@blp.route("/<int:user_id>", methods=["PATCH"])
@jwt_required()
@blp.arguments(UnitPrefsUpdateSchema)
@blp.response(200, UnitPrefsSchema)
def update_unit_prefs_for_user(payload: dict, user_id: int):
    if not _is_admin():
        abort(403, message="Only admin can update other users' unit prefs.")
    current = get_prefs_for_user(user_id)
    merged_dict = {**{k: v.value for k, v in current.__dict__.items()}, **(payload or {})}
    merged = prefs_from_dict(merged_dict)
    saved = set_prefs_for_user(user_id, merged)
    return _prefs_to_response(user_id, saved)
