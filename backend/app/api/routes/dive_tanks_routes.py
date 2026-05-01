# blueprint dive_tanks
from flask_smorest import Blueprint, abort
from flask import request
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required, get_jwt

from app.db import db
from app.models.dive_tank import DiveTank
from app.models.dive import Dive
from app.schemas import (
    DiveTankSchema,
    DiveTankCreateSchema,
    DiveTankUpdateSchema,
)

from app.utils.jwt import get_identity
from app.models.tank import Tank
from app.models.gas_mix import GasMix


blp = Blueprint(
    "dive_tanks",
    __name__,
    url_prefix="/api/v1/dive-tanks",
    description="Dive ↔ Tank mapping",
)


def _paginate(query):
    page = max(int(request.args.get("page", 1)), 1)
    page_size = min(max(int(request.args.get("page_size", 50)), 1), 500)
    items = query.limit(page_size).offset((page - 1) * page_size).all()
    return items, {"count": query.count(), "page": page, "page_size": page_size}


def _is_admin() -> bool:
    claims = get_jwt()
    return (claims.get("role") or "").lower() == "admin"


def _check_dive_owner(dive_id: int, user_id: int, admin: bool):
    if admin:
        return
    dive = db.session.get(Dive, dive_id)
    if not dive:
        abort(404, message="Dive not found")
    if int(dive.user_id) != int(user_id):
        abort(403, message="Access denied.")


def _check_tank_owner(tank_id: int, user_id: int, admin: bool):
    if admin or tank_id is None:
        return
    tank = db.session.get(Tank, tank_id)
    if not tank:
        abort(404, message="Tank not found")
    if int(tank.user_id) != int(user_id):
        abort(403, message="Tank does not belong to this user.")


def _check_gas_owner(gas_mix_id: int, user_id: int, admin: bool):
    if admin or gas_mix_id is None:
        return
    gas = db.session.get(GasMix, gas_mix_id)
    if not gas:
        abort(404, message="GasMix not found")
    if int(gas.user_id) != int(user_id):
        abort(403, message="GasMix does not belong to this user.")


@blp.route("/")
@jwt_required()
@blp.response(200, DiveTankSchema(many=True))
def list_dive_tanks():
    user_id = get_identity()
    admin = _is_admin()

    q = db.session.query(DiveTank)
    if dive_id := request.args.get("dive_id"):
        dive_id = int(dive_id)
        q = q.filter(DiveTank.dive_id == dive_id)
        if not admin:
            _check_dive_owner(dive_id, user_id, admin)
    else:
        if not admin:
            q = (
                q.join(Dive, Dive.dive_id == DiveTank.dive_id)
                 .filter(Dive.user_id == user_id)
            )

    q = q.order_by(DiveTank.dive_id.asc(), DiveTank.dive_tank_id.asc())
    items, meta = _paginate(q)
    return items, 200, {"X-Total-Count": str(meta["count"])}


@blp.route("/", methods=["POST"])
@jwt_required()
@blp.arguments(DiveTankCreateSchema)
@blp.response(201, DiveTankSchema)
def create_dive_tank(payload):
    user_id = int(get_identity())
    admin = _is_admin()
    dive_id = getattr(payload, "dive_id", None)
    tank_id = getattr(payload, "tank_id", None)
    gas_mix_id = getattr(payload, "gas_mix_id", None)

    if not dive_id:
        abort(400, message="dive_id is required")
    if not tank_id:
        abort(400, message="tank_id is required")
    if not gas_mix_id:
        abort(400, message="gas_mix_id is required")

    _check_dive_owner(int(dive_id), user_id, admin)
    _check_tank_owner(int(tank_id), user_id, admin)
    _check_gas_owner(int(gas_mix_id), user_id, admin)

    db.session.add(payload)
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        abort(400, message=str(e.orig))
    return payload


@blp.route("/<int:dive_tank_id>")
@jwt_required()
@blp.response(200, DiveTankSchema)
def get_dive_tank(dive_tank_id):
    user_id = get_identity()
    admin = _is_admin()

    obj = db.session.get(DiveTank, dive_tank_id)
    if not obj:
        abort(404, message="DiveTank not found")

    _check_dive_owner(int(obj.dive_id), user_id, admin)
    return obj


@blp.route("/<int:dive_tank_id>", methods=["PATCH"])
@jwt_required()
@blp.arguments(DiveTankUpdateSchema)
@blp.response(200, DiveTankSchema)
def update_dive_tank(payload, dive_tank_id):
    user_id = get_identity()
    admin = _is_admin()

    obj = db.session.get(DiveTank, dive_tank_id)
    if not obj:
        abort(404, message="DiveTank not found")

    _check_dive_owner(int(obj.dive_id), user_id, admin)
    if "tank_id" in payload:
        _check_tank_owner(payload.get("tank_id"), user_id, admin)
    if "gas_mix_id" in payload:
        _check_gas_owner(payload.get("gas_mix_id"), user_id, admin)

    for k, v in payload.items():
        setattr(obj, k, v)
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        abort(400, message=str(e.orig))
    return obj


@blp.route("/<int:dive_tank_id>", methods=["DELETE"])
@jwt_required()
@blp.response(204)
def delete_dive_tank(dive_tank_id):
    user_id = get_identity()
    admin = _is_admin()

    obj = db.session.get(DiveTank, dive_tank_id)
    if not obj:
        abort(404, message="DiveTank not found")

    _check_dive_owner(int(obj.dive_id), user_id, admin)
    db.session.delete(obj)
    db.session.commit()
    return ""


