# blueprint devices s prefixem /api/v1/
from flask_smorest import Blueprint, abort
from flask import request
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required, get_jwt

from app.db import db
from app.models.device import Device
from app.schemas import DeviceSchema, DeviceCreateSchema, DeviceUpdateSchema
from app.utils.jwt import get_identity


blp = Blueprint(
    "devices",
    __name__,
    url_prefix="/api/v1/devices",
    description="Dive computers & devices (user-owned)",
)


def _paginate(query):
    page = max(int(request.args.get("page", 1)), 1)
    page_size = min(max(int(request.args.get("page_size", 50)), 1), 200)
    items = query.limit(page_size).offset((page - 1) * page_size).all()
    return items, {"page": page, "page_size": page_size, "count": query.count()}


def _is_admin() -> bool:
    claims = get_jwt()
    return (claims.get("role") or "").lower() == "admin"


def _can_access(obj: Device, user_id: int) -> bool: # vraci True pokud ma uzivatel pristup k zarizeni
    return _is_admin() or obj.user_id == user_id


@blp.route("/")
@jwt_required()
@blp.response(200, DeviceSchema(many=True))
def list_devices():
    user_id = int(get_identity())
    q = db.session.query(Device)

    # ownership: user jen svoje, admin vse
    if not _is_admin():
        q = q.filter(Device.user_id == user_id)
    if brand := request.args.get("brand"):
        q = q.filter(Device.brand.ilike(f"%{brand}%"))
    if model := request.args.get("model"):
        q = q.filter(Device.model.ilike(f"%{model}%"))

    q = q.order_by(Device.brand.asc(), Device.model.asc())

    items, meta = _paginate(q)
    return items, 200, {"X-Total-Count": str(meta["count"])}


@blp.route("/", methods=["POST"])
@jwt_required()
@blp.arguments(DeviceCreateSchema)
@blp.response(201, DeviceSchema)
def create_device(payload):
    user_id = int(get_identity())

    obj = Device(user_id=user_id, **payload)
    db.session.add(obj)
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        abort(400, message=str(e.orig))
    return obj


@blp.route("/<int:device_id>")
@jwt_required()
@blp.response(200, DeviceSchema)
def get_device(device_id):
    user_id = int(get_identity())

    obj = db.session.get(Device, device_id)
    if not obj:
        abort(404, message="Device not found")
    if not _can_access(obj, user_id):
        abort(403, message="Not allowed")
    return obj


@blp.route("/<int:device_id>", methods=["PATCH"])
@jwt_required()
@blp.arguments(DeviceUpdateSchema)
@blp.response(200, DeviceSchema)
def update_device(payload, device_id):
    user_id = int(get_identity())
    obj = db.session.get(Device, device_id)
    if not obj:
        abort(404, message="Device not found")
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


@blp.route("/<int:device_id>", methods=["DELETE"])
@jwt_required()
@blp.response(204)
def delete_device(device_id):
    user_id = int(get_identity())

    obj = db.session.get(Device, device_id)
    if not obj:
        abort(404, message="Device not found")
    if not _can_access(obj, user_id):
        abort(403, message="Not allowed")
    db.session.delete(obj)
    db.session.commit()
    return ""
