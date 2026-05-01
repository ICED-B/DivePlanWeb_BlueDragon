# blueprint equipment_items
from flask_smorest import Blueprint, abort
from flask import request
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required, get_jwt
from sqlalchemy import distinct

from app.db import db
from app.models.equipment_item import EquipmentItem
from app.schemas import EquipmentItemSchema, EquipmentItemCreateSchema, EquipmentItemUpdateSchema
from app.utils.jwt import get_identity

blp = Blueprint(
    "equipment_items",
    __name__,
    url_prefix="/api/v1/equipment-items",
    description="Equipment inventory",
)


def _paginate(q):
    page = max(int(request.args.get("page", 1)), 1)
    size = min(max(int(request.args.get("page_size", 50)), 1), 500)
    items = q.limit(size).offset((page - 1) * size).all()
    return items, {"count": q.count(), "page": page, "page_size": size}


def _is_admin() -> bool:
    claims = get_jwt()
    return (claims.get("role") or "").lower() == "admin"


def _apply_owner_filter(q, user_id: int, admin: bool):
    if admin:
        return q
    return q.filter(EquipmentItem.user_id == user_id)


def _check_owner(obj: EquipmentItem, user_id: int, admin: bool):
    if admin:
        return
    if int(obj.user_id) != int(user_id):
        abort(403, message="Přístup odepřen.")


@blp.route("/")
@jwt_required()
@blp.response(200, EquipmentItemSchema(many=True))
def list_items():
    user_id = get_identity()
    admin = _is_admin()
    q = db.session.query(EquipmentItem)
    uid = request.args.get("user_id")
    if uid:
        uid = int(uid)
        if not admin and uid != int(user_id):
            abort(403, message="Přístup odepřen.")
        q = q.filter(EquipmentItem.user_id == uid)
    else:
        q = _apply_owner_filter(q, user_id, admin)

    if category := request.args.get("category"):
        q = q.filter(EquipmentItem.category == category)

    q = q.order_by(EquipmentItem.category.asc(), EquipmentItem.brand.asc())
    items, meta = _paginate(q)
    return items, 200, {"X-Total-Count": str(meta["count"])}


@blp.route("/me")
@jwt_required()
@blp.response(200, EquipmentItemSchema(many=True))
def list_my_items():
    user_id = get_identity()
    q = db.session.query(EquipmentItem).filter(EquipmentItem.user_id == user_id).order_by(
        EquipmentItem.category.asc(),
        EquipmentItem.brand.asc(),
    )
    items, meta = _paginate(q)
    return items, 200, {"X-Total-Count": str(meta["count"])}


@blp.route("/categories")
@jwt_required()
def list_categories():
    user_id = get_identity()
    admin = _is_admin()
    q = db.session.query(EquipmentItem)
    q = _apply_owner_filter(q, user_id, admin)
    rows = q.with_entities(distinct(EquipmentItem.category)).all()
    return [r[0] for r in rows if r[0]]


@blp.route("/", methods=["POST"])
@jwt_required()
@blp.arguments(EquipmentItemCreateSchema)
@blp.response(201, EquipmentItemSchema)
def create_item(payload):
    user_id = get_identity()
    payload["user_id"] = user_id

    obj = EquipmentItem(**payload)
    db.session.add(obj)
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        abort(400, message=str(e.orig))
    return obj


@blp.route("/<int:equipment_id>")
@jwt_required()
@blp.response(200, EquipmentItemSchema)
def get_item(equipment_id):
    user_id = get_identity()
    admin = _is_admin()
    obj = db.session.get(EquipmentItem, equipment_id)
    if not obj:
        abort(404, message="EquipmentItem not found")
    _check_owner(obj, user_id, admin)
    return obj


@blp.route("/<int:equipment_id>", methods=["PATCH"])
@jwt_required()
@blp.arguments(EquipmentItemUpdateSchema)
@blp.response(200, EquipmentItemSchema)
def update_item(payload, equipment_id):
    user_id = get_identity()
    admin = _is_admin()

    obj = db.session.get(EquipmentItem, equipment_id)
    if not obj:
        abort(404, message="EquipmentItem not found")

    _check_owner(obj, user_id, admin)

    payload.pop("user_id", None)
    for k, v in payload.items():
        setattr(obj, k, v)

    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        abort(400, message=str(e.orig))
    return obj


@blp.route("/<int:equipment_id>", methods=["DELETE"])
@jwt_required()
@blp.response(204)
def delete_item(equipment_id):
    user_id = get_identity()
    admin = _is_admin()
    obj = db.session.get(EquipmentItem, equipment_id)
    if not obj:
        abort(404, message="EquipmentItem not found")
    _check_owner(obj, user_id, admin)
    db.session.delete(obj)
    db.session.commit()
    return ""
