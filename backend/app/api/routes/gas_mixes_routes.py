# blueprint gas_mixes
from flask_smorest import Blueprint, abort
from flask import request
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required, get_jwt

from app.db import db
from app.models.gas_mix import GasMix
from app.schemas import (
    GasMixSchema, GasMixCreateSchema, GasMixUpdateSchema,
)
from app.utils.jwt import get_identity

blp = Blueprint("gas_mixes", __name__,
                url_prefix="/api/v1/gases", description="Gas mixes")


def _paginate(query):
    page = max(int(request.args.get("page", 1)), 1)
    page_size = min(max(int(request.args.get("page_size", 50)), 1), 200)
    items = query.limit(page_size).offset((page - 1) * page_size).all()
    return items, {"page": page, "page_size": page_size, "count": query.count()}


def _is_admin() -> bool:
    claims = get_jwt()
    return (claims.get("role") or "").lower() == "admin"


def _can_access(obj: GasMix, user_id: int) -> bool:
    return _is_admin() or int(obj.user_id) == int(user_id)


@blp.route("/")
@jwt_required()
@blp.response(200, GasMixSchema(many=True))
def list_gases():
    user_id = int(get_identity())
    q = db.session.query(GasMix)
    # ownership, uzivatel vidi jen svoje smesi
    if not _is_admin():
        q = q.filter(GasMix.user_id == user_id)

    # volitelny filtr na aktivni smesi
    if only_active := request.args.get("active"):
        if only_active.lower() in ("1", "true", "yes"):
            q = q.filter(GasMix.active.is_(True))

    q = q.order_by(GasMix.gas_type, GasMix.o2_percent, GasMix.he_percent)
    items, meta = _paginate(q)
    return items, 200, {"X-Total-Count": str(meta["count"])}


@blp.route("/", methods=["POST"])
@jwt_required()
@blp.arguments(GasMixCreateSchema)
@blp.response(201, GasMixSchema)
def create_gas(payload):
    user_id = int(get_identity())
    obj = GasMix(user_id=user_id, **payload)
    db.session.add(obj)
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        abort(400, message=str(e.orig))
    return obj


@blp.route("/<int:gas_mix_id>")
@jwt_required()
@blp.response(200, GasMixSchema)
def get_gas(gas_mix_id):
    user_id = int(get_identity())
    obj = db.session.get(GasMix, gas_mix_id)
    if not obj:
        abort(404, message="Gas mix not found")
    if not _can_access(obj, user_id):
        abort(403, message="Not allowed")
    return obj


@blp.route("/<int:gas_mix_id>", methods=["PATCH"])
@jwt_required()
@blp.arguments(GasMixUpdateSchema)
@blp.response(200, GasMixSchema)
def update_gas(payload, gas_mix_id):
    user_id = int(get_identity())
    obj = db.session.get(GasMix, gas_mix_id)
    if not obj:
        abort(404, message="Gas mix not found")
    if not _can_access(obj, user_id):
        abort(403, message="Not allowed")

    for k, v in payload.items():
        setattr(obj, k, v)
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        abort(400, message=str(e.orig))
    return obj


@blp.route("/<int:gas_mix_id>", methods=["DELETE"])
@jwt_required()
@blp.response(204)
def delete_gas(gas_mix_id):
    user_id = int(get_identity())
    obj = db.session.get(GasMix, gas_mix_id)
    if not obj:
        abort(404, message="Gas mix not found")
    if not _can_access(obj, user_id):
        abort(403, message="Not allowed")
    db.session.delete(obj)
    db.session.commit()
    return ""


