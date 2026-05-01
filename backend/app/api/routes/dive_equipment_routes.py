# blueprint dive_equipment prefix /api/v1/
from flask_smorest import Blueprint, abort
from flask import request
from flask_jwt_extended import jwt_required, get_jwt

from app.db import db
from app.models.dive_equipment import DiveEquipment
from app.models.dive import Dive
from app.schemas import DiveEquipmentSchema, DiveEquipmentCreateSchema
from app.utils.jwt import get_identity
from app.models.equipment_item import EquipmentItem


blp = Blueprint(
    "dive_equipment",
    __name__,
    url_prefix="/api/v1/dive-equipment",
    description="Dive ↔ Equipment mapping",
)


def _paginate(q):
    page = max(int(request.args.get("page", 1)), 1)
    size = min(max(int(request.args.get("page_size", 100)), 1), 1000)
    items = q.limit(size).offset((page - 1) * size).all()
    return items, {"count": q.count(), "page": page, "page_size": size}


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


def _check_equipment_owner(equipment_id: int, user_id: int, admin: bool):
    if admin:
        return
    eq = db.session.get(EquipmentItem, equipment_id)
    if not eq:
        abort(404, message="EquipmentItem not found")
    if int(eq.user_id) != int(user_id):
        abort(403, message="Equipment does not belong to this user.")


@blp.route("/")
@jwt_required()
@blp.response(200, DiveEquipmentSchema(many=True))
def list_dive_equipment():
    user_id = get_identity()
    admin = _is_admin()
    q = db.session.query(DiveEquipment)
    if dive_id := request.args.get("dive_id"):
        dive_id = int(dive_id)
        q = q.filter(DiveEquipment.dive_id == dive_id)
        if not admin:
            _check_dive_owner(dive_id, user_id, admin)
    else:
        if not admin:
            q = (
                q.join(Dive, Dive.dive_id == DiveEquipment.dive_id)
                 .filter(Dive.user_id == user_id)
            )

    if equipment_id := request.args.get("equipment_id"):
        q = q.filter(DiveEquipment.equipment_id == int(equipment_id))

    items, meta = _paginate(q.order_by(
        DiveEquipment.dive_id.asc(), DiveEquipment.equipment_id.asc()))
    return items, 200, {"X-Total-Count": str(meta["count"])}


@blp.route("/", methods=["POST"])
@jwt_required()
@blp.arguments(DiveEquipmentCreateSchema)
@blp.response(201, DiveEquipmentSchema)
def create_dive_equipment(payload):
    user_id = int(get_identity())
    admin = _is_admin()
    dive_id = getattr(payload, "dive_id", None)
    equipment_id = getattr(payload, "equipment_id", None)

    if not dive_id:
        abort(400, message="dive_id is required")
    if not equipment_id:
        abort(400, message="equipment_id is required")

    _check_dive_owner(int(dive_id), user_id, admin)
    _check_equipment_owner(int(equipment_id), user_id, admin)

    db.session.add(payload)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        abort(400, message=str(e))

    return payload


@blp.route("/<int:dive_id>/<int:equipment_id>", methods=["DELETE"])
@jwt_required()
@blp.response(204)
def delete_dive_equipment(dive_id, equipment_id):
    user_id = get_identity()
    admin = _is_admin()

    obj = db.session.query(DiveEquipment).get((dive_id, equipment_id))
    if not obj:
        abort(404, message="DiveEquipment not found")

    _check_dive_owner(int(dive_id), user_id, admin)
    _check_equipment_owner(int(equipment_id), user_id, admin)

    db.session.delete(obj)
    db.session.commit()
    return ""
