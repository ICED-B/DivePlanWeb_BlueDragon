# blueprint media
from flask_smorest import Blueprint, abort
from flask import request
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required, get_jwt

from app.db import db
from app.models.media import Media
from app.models.dive import Dive
from app.schemas import MediaSchema, MediaCreateSchema, MediaUpdateSchema
from app.utils.jwt import get_identity

blp = Blueprint(
    "media",
    __name__,
    url_prefix="/api/v1/media",
    description="Media attached to dives",
)


def _paginate(q):
    page = max(int(request.args.get("page", 1)), 1)
    size = min(max(int(request.args.get("page_size", 50)), 1), 500)
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


@blp.route("/")
@jwt_required()
@blp.response(200, MediaSchema(many=True))
def list_media():
    user_id = get_identity()
    admin = _is_admin()

    q = db.session.query(Media)

    if dive_id := request.args.get("dive_id"):
        dive_id = int(dive_id)
        q = q.filter(Media.dive_id == dive_id)
        if not admin:
            _check_dive_owner(dive_id, user_id, admin)
    else:
        if not admin:
            q = q.join(Dive, Dive.dive_id == Media.dive_id).filter(
                Dive.user_id == user_id)

    q = q.order_by(Media.dive_id.asc(), Media.media_id.asc())
    items, meta = _paginate(q)
    return items, 200, {"X-Total-Count": str(meta["count"])}


@blp.route("/", methods=["POST"])
@jwt_required()
@blp.arguments(MediaCreateSchema)
@blp.response(201, MediaSchema)
def create_media(payload):
    user_id = int(get_identity())
    admin = _is_admin()
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


@blp.route("/<int:media_id>")
@jwt_required()
@blp.response(200, MediaSchema)
def get_media(media_id):
    user_id = get_identity()
    admin = _is_admin()
    obj = db.session.get(Media, media_id)
    if not obj:
        abort(404, message="Media not found")
    _check_dive_owner(int(obj.dive_id), user_id, admin)
    return obj


@blp.route("/<int:media_id>", methods=["PATCH"])
@jwt_required()
@blp.arguments(MediaUpdateSchema)
@blp.response(200, MediaSchema)
def update_media(payload, media_id):
    user_id = get_identity()
    admin = _is_admin()
    obj = db.session.get(Media, media_id)
    if not obj:
        abort(404, message="Media not found")
    _check_dive_owner(int(obj.dive_id), user_id, admin)

    for k, v in payload.items():
        setattr(obj, k, v)
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        abort(400, message=str(e.orig))
    return obj


@blp.route("/<int:media_id>", methods=["DELETE"])
@jwt_required()
@blp.response(204)
def delete_media(media_id):
    user_id = get_identity()
    admin = _is_admin()

    obj = db.session.get(Media, media_id)
    if not obj:
        abort(404, message="Media not found")
    _check_dive_owner(int(obj.dive_id), user_id, admin)
    db.session.delete(obj)
    db.session.commit()
    return ""
