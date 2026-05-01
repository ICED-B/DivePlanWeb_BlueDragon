# CRUD operace pro lahve Tank
from flask_smorest import Blueprint, abort
from flask import request
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required, get_jwt

from app.db import db
from app.models.tank import Tank
from app.schemas import TankSchema, TankCreateSchema, TankUpdateSchema
from app.utils.jwt import get_identity

blp = Blueprint("tanks", __name__, url_prefix="/api/v1/tanks",
                description="Cylinders (user-owned)")


def _paginate(query):
    page = max(int(request.args.get("page", 1)), 1)
    page_size = min(max(int(request.args.get("page_size", 50)), 1), 200)
    items = query.limit(page_size).offset((page - 1) * page_size).all()
    return items, {"page": page, "page_size": page_size, "count": query.count()}


def _is_admin() -> bool:
    claims = get_jwt()
    return (claims.get("role") or "").lower() == "admin"


def _can_access(obj: Tank, user_id: int) -> bool:
    return _is_admin() or int(obj.user_id) == int(user_id)


@blp.route("/")
@jwt_required()
@blp.response(200, TankSchema(many=True))
def list_tanks():
    user_id = int(get_identity())
    q = db.session.query(Tank)

    if not _is_admin():
        q = q.filter(Tank.user_id == user_id)

    q = q.order_by(Tank.volume_l.desc().nullslast())
    items, meta = _paginate(q)
    return items, 200, {"X-Total-Count": str(meta["count"])}


@blp.route("/", methods=["POST"])
@jwt_required()
@blp.arguments(TankCreateSchema)
@blp.response(201, TankSchema)
def create_tank(payload):
    user_id = int(get_identity())
    obj = Tank(user_id=user_id, **payload)
    db.session.add(obj)
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        abort(400, message=str(e.orig))
    return obj


@blp.route("/<int:tank_id>")
@jwt_required()
@blp.response(200, TankSchema)
def get_tank(tank_id):
    user_id = int(get_identity())
    obj = db.session.get(Tank, tank_id)
    if not obj:
        abort(404, message="Tank not found")
    if not _can_access(obj, user_id):
        abort(403, message="Not allowed")
    return obj


@blp.route("/<int:tank_id>", methods=["PATCH"])
@jwt_required()
@blp.arguments(TankUpdateSchema)
@blp.response(200, TankSchema)
def update_tank(payload, tank_id):
    user_id = int(get_identity())
    obj = db.session.get(Tank, tank_id)
    if not obj:
        abort(404, message="Tank not found")
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


@blp.route("/<int:tank_id>", methods=["DELETE"])
@jwt_required()
@blp.response(204)
def delete_tank(tank_id):
    user_id = int(get_identity())
    obj = db.session.get(Tank, tank_id)
    if not obj:
        abort(404, message="Tank not found")
    if not _can_access(obj, user_id):
        abort(403, message="Not allowed")
    db.session.delete(obj)
    db.session.commit()
    return ""
