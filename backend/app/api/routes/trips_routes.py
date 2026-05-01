# CRUD operace Trip
from flask_smorest import Blueprint, abort
from flask import request
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required, get_jwt

from app.db import db
from app.models.trip import Trip
from app.schemas import TripSchema, TripCreateSchema, TripUpdateSchema
from app.utils.jwt import get_identity

blp = Blueprint(
    "trips",
    __name__,
    url_prefix="/api/v1/trips",
    description="Trips CRUD",
)


def _paginate(q):
    page = max(int(request.args.get("page", 1)), 1)
    size = min(max(int(request.args.get("page_size", 50)), 1), 200)
    items = q.limit(size).offset((page - 1) * size).all()
    return items, {"count": q.count(), "page": page, "page_size": size}


def _is_admin() -> bool:
    claims = get_jwt()
    return (claims.get("role") or "").lower() == "admin"


def _check_owner(obj: Trip, user_id: int, admin: bool):
    if admin:
        return
    if int(obj.user_id) != int(user_id):
        abort(403, message="Access denied.")


@blp.route("/")
@jwt_required()
@blp.response(200, TripSchema(many=True))
def list_trips():
    current_id = get_identity()
    admin = _is_admin()

    q = db.session.query(Trip).order_by(
        Trip.start_date.desc().nullslast(), Trip.trip_id.desc())

    uid = request.args.get("user_id")
    if uid:
        uid = int(uid)
        if not admin and uid != int(current_id):
            abort(403, message="Access denied.")
        q = q.filter(Trip.user_id == uid)
    else:
        if not admin:
            q = q.filter(Trip.user_id == current_id)

    items, meta = _paginate(q)
    return items, 200, {"X-Total-Count": str(meta["count"])}


@blp.route("/", methods=["POST"])
@jwt_required()
@blp.arguments(TripCreateSchema)
@blp.response(201, TripSchema)
def create_trip(payload):
    current_id = get_identity()

    # user_id priradi automaticky podle prihlaseneho uzivatele
    payload["user_id"] = current_id
    obj = Trip(**payload)
    db.session.add(obj)
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        abort(400, message=str(e.orig))
    return obj


@blp.route("/<int:trip_id>")
@jwt_required()
@blp.response(200, TripSchema)
def get_trip(trip_id):
    current_id = get_identity()
    admin = _is_admin()

    obj = db.session.get(Trip, trip_id)
    if not obj:
        abort(404, message="Trip not found")

    _check_owner(obj, current_id, admin)
    return obj


@blp.route("/<int:trip_id>", methods=["PATCH"])
@jwt_required()
@blp.arguments(TripUpdateSchema)
@blp.response(200, TripSchema)
def update_trip(payload, trip_id):
    current_id = get_identity()
    admin = _is_admin()

    obj = db.session.get(Trip, trip_id)
    if not obj:
        abort(404, message="Trip not found")

    _check_owner(obj, current_id, admin)

    # Zabranime prepisani vlastnika
    payload.pop("user_id", None)
    for k, v in payload.items():
        setattr(obj, k, v)

    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        abort(400, message=str(e.orig))
    return obj


@blp.route("/<int:trip_id>", methods=["DELETE"])
@jwt_required()
@blp.response(204)
def delete_trip(trip_id):
    current_id = get_identity()
    admin = _is_admin()

    obj = db.session.get(Trip, trip_id)
    if not obj:
        abort(404, message="Trip not found")

    _check_owner(obj, current_id, admin)
    db.session.delete(obj)
    db.session.commit()
    return ""
