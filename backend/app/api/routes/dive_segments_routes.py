# Blueprint dive_segments s prefixem /api/v1/
from flask_smorest import Blueprint, abort
from flask import request
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required, get_jwt

from app.db import db
from app.models.dive_segment import DiveSegment
from app.models.dive import Dive
from app.schemas import (
    DiveSegmentSchema,
    DiveSegmentCreateSchema,
    DiveSegmentUpdateSchema,
)
from app.utils.jwt import get_identity
from app.models.dive_segment import DiveSegment
from app.models.dive import Dive
from app.models.gas_mix import GasMix

blp = Blueprint(
    "dive_segments",
    __name__,
    url_prefix="/api/v1/dive-segments",
    description="Dive segments (gas/CCR)",
)


def _paginate(query):
    page = max(int(request.args.get("page", 1)), 1)
    page_size = min(max(int(request.args.get("page_size", 100)), 1), 1000)
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


def _check_gas_owner(gas_mix_id: int, user_id: int, admin: bool):
    if admin or gas_mix_id is None:
        return
    gas = db.session.get(GasMix, int(gas_mix_id))
    if not gas:
        abort(404, message="GasMix not found")
    if int(gas.user_id) != int(user_id):
        abort(403, message="GasMix does not belong to this user.")


@blp.route("/")
@jwt_required()
@blp.response(200, DiveSegmentSchema(many=True))
def list_segments():
    user_id = get_identity()
    admin = _is_admin()

    q = db.session.query(DiveSegment)
    if dive_id := request.args.get("dive_id"):
        dive_id = int(dive_id)
        q = q.filter(DiveSegment.dive_id == dive_id)
        if not admin:
            _check_dive_owner(dive_id, user_id, admin)
    else:
        if not admin:
            q = (
                q.join(Dive, Dive.dive_id == DiveSegment.dive_id)
                 .filter(Dive.user_id == user_id)
            )

    q = q.order_by(DiveSegment.dive_id.asc(), DiveSegment.start_t_min.asc())
    items, meta = _paginate(q)
    return items, 200, {"X-Total-Count": str(meta["count"])}


@blp.route("/", methods=["POST"])
@jwt_required()
@blp.arguments(DiveSegmentCreateSchema)
@blp.response(201, DiveSegmentSchema)
def create_segment(payload):
    user_id = int(get_identity())
    admin = _is_admin()
    dive_id = getattr(payload, "dive_id", None)
    gas_mix_id = getattr(payload, "gas_mix_id", None)

    if not dive_id:
        abort(400, message="dive_id is required")

    _check_dive_owner(int(dive_id), user_id, admin)

    if gas_mix_id is not None:
        _check_gas_owner(int(gas_mix_id), user_id, admin)
    db.session.add(payload)
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        abort(400, message=str(e.orig))
    return payload


@blp.route("/<int:dive_segment_id>")
@jwt_required()
@blp.response(200, DiveSegmentSchema)
def get_segment(dive_segment_id):
    user_id = get_identity()
    admin = _is_admin()
    obj = db.session.get(DiveSegment, dive_segment_id)
    if not obj:
        abort(404, message="DiveSegment not found")
    _check_dive_owner(int(obj.dive_id), user_id, admin)
    return obj


@blp.route("/<int:dive_segment_id>", methods=["PATCH"])
@jwt_required()
@blp.arguments(DiveSegmentUpdateSchema)
@blp.response(200, DiveSegmentSchema)
def update_segment(payload, dive_segment_id):
    user_id = get_identity()
    admin = _is_admin()
    obj = db.session.get(DiveSegment, dive_segment_id)
    if not obj:
        abort(404, message="DiveSegment not found")

    _check_dive_owner(int(obj.dive_id), user_id, admin)
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


@blp.route("/<int:dive_segment_id>", methods=["DELETE"])
@jwt_required()
@blp.response(204)
def delete_segment(dive_segment_id):
    user_id = get_identity()
    admin = _is_admin()
    obj = db.session.get(DiveSegment, dive_segment_id)
    if not obj:
        abort(404, message="DiveSegment not found")
    _check_dive_owner(int(obj.dive_id), user_id, admin)
    db.session.delete(obj)
    db.session.commit()
    return ""
