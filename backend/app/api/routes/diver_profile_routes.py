# blueprint diver_profiles
from flask_smorest import Blueprint, abort
from flask import request
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required, get_jwt

from app.db import db
from app.models.diver_profile import DiverProfile
from app.schemas import DiverProfileSchema, DiverProfileCreateSchema, DiverProfileUpdateSchema

from app.services.unit_prefs_service import (
    get_prefs_for_user,
    set_prefs_for_user,
    prefs_to_dict,
    prefs_from_dict,
    UnitPrefsServiceError,
)

from app.utils.jwt import get_identity

blp = Blueprint(
    "diver_profiles",
    __name__,
    url_prefix="/api/v1/diver-profiles",
    description="User profiles (preferences & rates)",
)


def _paginate(q):
    page = max(int(request.args.get("page", 1)), 1)
    size = min(max(int(request.args.get("page_size", 50)), 1), 200)
    items = q.limit(size).offset((page - 1) * size).all()
    return items, {"count": q.count(), "page": page, "page_size": size}


def _is_admin() -> bool:
    claims = get_jwt()
    return (claims.get("role") or "").lower() == "admin"


@blp.route("/")
@jwt_required()
@blp.response(200, DiverProfileSchema(many=True))
def list_profiles():
    current_id = get_identity()
    admin = _is_admin()
    q = db.session.query(DiverProfile)
    uid = request.args.get("user_id")       # volitelny filtr, uzivatel muze filtrovat jen sebe
    if uid:
        uid = int(uid)
        if not admin and uid != int(current_id):
            abort(403, message="Access denied.")
        q = q.filter(DiverProfile.user_id == uid)
    else:
        if not admin:
            q = q.filter(DiverProfile.user_id == current_id)

    items, meta = _paginate(q.order_by(DiverProfile.profile_id.asc()))
    return items, 200, {"X-Total-Count": str(meta["count"])}


@blp.route("/", methods=["POST"])
@jwt_required()
@blp.arguments(DiverProfileCreateSchema)
@blp.response(201, DiverProfileSchema)
def create_profile(payload):
    current_id = get_identity()
    existing = db.session.query(DiverProfile).filter(
        DiverProfile.user_id == current_id).first()    # vztah 1:1 pri existujicim profilu vrat 409
    if existing:
        abort(409, message="Profile already exists for this user.")

    payload["user_id"] = current_id
    obj = DiverProfile(**payload)
    db.session.add(obj)

    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        abort(400, message=str(e.orig))
    return obj


@blp.route("/<int:profile_id>")
@jwt_required()
@blp.response(200, DiverProfileSchema)
def get_profile(profile_id):
    current_id = get_identity()
    admin = _is_admin()

    obj = db.session.get(DiverProfile, profile_id)
    if not obj:
        abort(404, message="DiverProfile not found")

    if not admin and int(obj.user_id) != int(current_id):
        abort(403, message="Access denied.")
    return obj


@blp.route("/<int:profile_id>", methods=["PATCH"])
@jwt_required()
@blp.arguments(DiverProfileUpdateSchema)
@blp.response(200, DiverProfileSchema)
def update_profile(payload, profile_id):
    current_id = get_identity()
    admin = _is_admin()

    obj = db.session.get(DiverProfile, profile_id)
    if not obj:
        abort(404, message="DiverProfile not found")

    if not admin and int(obj.user_id) != int(current_id):
        abort(403, message="Access denied.")

    payload.pop("user_id", None)
    for k, v in payload.items():
        setattr(obj, k, v)

    db.session.commit()
    return obj


@blp.route("/<int:profile_id>", methods=["DELETE"])
@jwt_required()
@blp.response(204)
def delete_profile(profile_id):
    current_id = get_identity()
    admin = _is_admin()
    obj = db.session.get(DiverProfile, profile_id)
    if not obj:
        abort(404, message="DiverProfile not found")
    if not admin and int(obj.user_id) != int(current_id):
        abort(403, message="Access denied.")
    db.session.delete(obj)
    db.session.commit()
    return ""
