# blueprint equipment_services
from flask_smorest import Blueprint, abort
from flask import request
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required, get_jwt

from app.db import db
from app.models.equipment_service import EquipmentService
from app.models.equipment_item import EquipmentItem
from app.schemas import (
    EquipmentServiceSchema,
    EquipmentServiceCreateSchema,
    EquipmentServiceUpdateSchema,
)
from app.utils.jwt import get_identity

blp = Blueprint(
    "equipment_services",
    __name__,
    url_prefix="/api/v1/equipment-services",
    description="Equipment service & maintenance",
)


def _paginate(q):
    page = max(int(request.args.get("page", 1)), 1)
    size = min(max(int(request.args.get("page_size", 50)), 1), 500)
    items = q.limit(size).offset((page - 1) * size).all()
    return items, {"count": q.count(), "page": page, "page_size": size}


def _is_admin() -> bool:
    claims = get_jwt()
    return (claims.get("role") or "").lower() == "admin"


def _owner_condition(user_id: int):
    return EquipmentItem.user_id == user_id


@blp.route("/")
@jwt_required()
@blp.response(200, EquipmentServiceSchema(many=True))
def list_services():
    user_id = int(get_identity())
    admin = _is_admin()

    # join na EquipmentItem zajistuje kontrolu vlastnictvi
    q = (
        db.session.query(EquipmentService)
        .join(
            EquipmentItem,
            EquipmentItem.equipment_id == EquipmentService.equipment_id,
        )
    )
    if not admin:
        q = q.filter(_owner_condition(user_id))
    if equipment_id := request.args.get("equipment_id"):
        q = q.filter(EquipmentService.equipment_id == int(equipment_id))
    q = q.order_by(EquipmentService.next_service.asc().nullslast())
    items, meta = _paginate(q)
    return items, 200, {"X-Total-Count": str(meta["count"])}


@blp.route("/due")
@jwt_required()
@blp.response(200, EquipmentServiceSchema(many=True))
def list_due_services():
    from datetime import date, timedelta
    user_id = int(get_identity())
    admin = _is_admin()
    days = int(request.args.get("days", 30))
    today = date.today()
    limit_date = today + timedelta(days=days)

    q = (
        db.session.query(EquipmentService)
        .join(
            EquipmentItem,
            EquipmentItem.equipment_id == EquipmentService.equipment_id,  # FIX
        )
    )

    if not admin:
        q = q.filter(_owner_condition(user_id))
    q = q.filter(
        EquipmentService.next_service.isnot(None),
        EquipmentService.next_service <= limit_date,
    ).order_by(EquipmentService.next_service.asc())
    return q.all()


@blp.route("/", methods=["POST"])
@jwt_required()
@blp.arguments(EquipmentServiceCreateSchema)
@blp.response(201, EquipmentServiceSchema)
def create_service(payload):
    user_id = int(get_identity())
    admin = _is_admin()

    # payload je EquipmentService instance (load_instance=True)
    equipment_id = getattr(payload, "equipment_id", None)
    if not equipment_id:
        abort(400, message="equipment_id is required")
    item_q = db.session.query(EquipmentItem).filter(
        EquipmentItem.equipment_id == int(equipment_id)
    )

    if not admin:
        item_q = item_q.filter(_owner_condition(user_id))

    item = item_q.first()
    if not item:
        abort(403, message="Nemůžeš vytvářet servis pro cizí vybavení.")
    db.session.add(payload)
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        abort(400, message=str(e.orig))
    return payload


@blp.route("/<int:service_id>")
@jwt_required()
@blp.response(200, EquipmentServiceSchema)
def get_service(service_id):
    user_id = int(get_identity())
    admin = _is_admin()

    q = (
        db.session.query(EquipmentService)
        .join(
            EquipmentItem,
            EquipmentItem.equipment_id == EquipmentService.equipment_id,  # FIX
        )
        .filter(EquipmentService.service_id == service_id)  # FIX
    )

    if not admin:
        q = q.filter(_owner_condition(user_id))

    obj = q.first()
    if not obj:
        abort(404, message="EquipmentService not found")
    return obj


@blp.route("/<int:service_id>", methods=["PATCH"])
@jwt_required()
@blp.arguments(EquipmentServiceUpdateSchema)
@blp.response(200, EquipmentServiceSchema)
def update_service(payload, service_id):
    user_id = int(get_identity())
    admin = _is_admin()

    q = (
        db.session.query(EquipmentService)
        .join(
            EquipmentItem,
            EquipmentItem.equipment_id == EquipmentService.equipment_id,  # FIX
        )
        .filter(EquipmentService.service_id == service_id)  # FIX
    )
    if not admin:
        q = q.filter(_owner_condition(user_id))
    obj = q.first()
    if not obj:
        abort(404, message="EquipmentService not found")
    for k, v in payload.items():
        setattr(obj, k, v)
    db.session.commit()
    return obj


@blp.route("/<int:service_id>", methods=["DELETE"])
@jwt_required()
@blp.response(204)
def delete_service(service_id):
    user_id = int(get_identity())
    admin = _is_admin()

    q = (
        db.session.query(EquipmentService)
        .join(
            EquipmentItem,
            EquipmentItem.equipment_id == EquipmentService.equipment_id,  # FIX
        )
        .filter(EquipmentService.service_id == service_id)  # FIX
    )
    if not admin:
        q = q.filter(_owner_condition(user_id))
    obj = q.first()
    if not obj:
        abort(404, message="EquipmentService not found")
    db.session.delete(obj)
    db.session.commit()
    return ""
