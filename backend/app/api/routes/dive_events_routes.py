# blueprint dive_events s prefixem /api/v1/
from flask_smorest import Blueprint, abort
from flask import request
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required, get_jwt

from app.db import db
from app.models.dive_event import DiveEvent
from app.models.dive import Dive
from app.schemas import (
    DiveEventSchema,
    DiveEventCreateSchema,
    DiveEventUpdateSchema,
)
from app.utils.jwt import get_identity

blp = Blueprint(
    "dive_events",
    __name__,
    url_prefix="/api/v1/dive-events",
    description="Dive events",
)


def _paginate(query):
    page = max(int(request.args.get("page", 1)), 1)
    page_size = min(max(int(request.args.get("page_size", 200)), 1), 2000)
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


@blp.route("/")
@jwt_required()
@blp.response(200, DiveEventSchema(many=True))
def list_events():
    user_id = get_identity()
    admin = _is_admin()
    q = db.session.query(DiveEvent)
    if dive_id := request.args.get("dive_id"):
        dive_id = int(dive_id)
        q = q.filter(DiveEvent.dive_id == dive_id)
        if not admin:
            _check_dive_owner(dive_id, user_id, admin)
    else:
        if not admin:
            q = q.join(Dive, Dive.dive_id == DiveEvent.dive_id).filter(
                Dive.user_id == user_id)

    q = q.order_by(DiveEvent.dive_id.asc(), DiveEvent.t_min.asc())
    items, meta = _paginate(q)
    return items, 200, {"X-Total-Count": str(meta["count"])}


@blp.route("/", methods=["POST"])
@jwt_required()
@blp.arguments(DiveEventCreateSchema)
@blp.response(201, DiveEventSchema)
def create_event(payload):
    user_id = int(get_identity())
    admin = _is_admin()

    # payload je DiveEvent instance (load_instance=True)
    dive_id = getattr(payload, "dive_id", None)
    if not dive_id:
        abort(400, message="dive_id is required")

    _check_dive_owner(int(dive_id), user_id, admin)

    db.session.add(payload)
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        abort(400, message=str(e.orig))
    return payload


@blp.route("/<int:event_id>")
@jwt_required()
@blp.response(200, DiveEventSchema)
def get_event(event_id):
    user_id = get_identity()
    admin = _is_admin()
    obj = db.session.get(DiveEvent, event_id)
    if not obj:
        abort(404, message="DiveEvent not found")
    _check_dive_owner(int(obj.dive_id), user_id, admin)
    return obj


@blp.route("/<int:event_id>", methods=["PATCH"])
@jwt_required()
@blp.arguments(DiveEventUpdateSchema)
@blp.response(200, DiveEventSchema)
def update_event(payload, event_id):
    user_id = get_identity()
    admin = _is_admin()
    obj = db.session.get(DiveEvent, event_id)
    if not obj:
        abort(404, message="DiveEvent not found")

    _check_dive_owner(int(obj.dive_id), user_id, admin)
    for k, v in payload.items():
        setattr(obj, k, v)
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        abort(400, message=str(e.orig))
    return obj


@blp.route("/<int:event_id>", methods=["DELETE"])
@jwt_required()
@blp.response(204)
def delete_event(event_id):
    user_id = get_identity()
    admin = _is_admin()

    obj = db.session.get(DiveEvent, event_id)
    if not obj:
        abort(404, message="DiveEvent not found")

    _check_dive_owner(int(obj.dive_id), user_id, admin)
    db.session.delete(obj)
    db.session.commit()
    return ""
