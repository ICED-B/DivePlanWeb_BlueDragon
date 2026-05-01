# CRUD operace uzivatele s tagy
from flask_smorest import Blueprint, abort
from flask import request
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required, get_jwt

from app.db import db
from app.models.tag import Tag
from app.schemas import TagSchema, TagCreateSchema, TagUpdateSchema
from app.utils.jwt import get_identity

blp = Blueprint(
    "tags",
    __name__,
    url_prefix="/api/v1/tags",
    description="User tags",
)


def _paginate(q):
    page = max(int(request.args.get("page", 1)), 1)
    size = min(max(int(request.args.get("page_size", 100)), 1), 1000)
    items = q.limit(size).offset((page - 1) * size).all()
    return items, {"count": q.count(), "page": page, "page_size": size}


def _is_admin() -> bool:
    claims = get_jwt()
    return (claims.get("role") or "").lower() == "admin"


@blp.route("/")
@jwt_required()
@blp.response(200, TagSchema(many=True))
def list_tags():
    user_id = get_identity()
    admin = _is_admin()

    q = db.session.query(Tag).order_by(Tag.name.asc())

    uid = request.args.get("user_id")
    if uid:
        uid = int(uid)
        if not admin and uid != int(user_id):
            abort(403, message="Access denied.")
        q = q.filter(Tag.user_id == uid)
    else:
        if not admin:
            q = q.filter(Tag.user_id == user_id)

    items, meta = _paginate(q)
    return items, 200, {"X-Total-Count": str(meta["count"])}


@blp.route("/", methods=["POST"])
@jwt_required()
@blp.arguments(TagCreateSchema)
@blp.response(201, TagSchema)
def create_tag(payload):
    user_id = int(get_identity())
    payload.user_id = user_id

    db.session.add(payload)
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        abort(400, message=str(e.orig))
    return payload


@blp.route("/<int:tag_id>")
@jwt_required()
@blp.response(200, TagSchema)
def get_tag(tag_id):
    user_id = get_identity()
    admin = _is_admin()

    obj = db.session.get(Tag, tag_id)
    if not obj:
        abort(404, message="Tag not found")
    if not admin and int(obj.user_id) != int(user_id):
        abort(403, message="Access denied.")
    return obj


@blp.route("/<int:tag_id>", methods=["PATCH"])
@jwt_required()
@blp.arguments(TagUpdateSchema)
@blp.response(200, TagSchema)
def update_tag(payload, tag_id):
    user_id = get_identity()
    admin = _is_admin()

    obj = db.session.get(Tag, tag_id)
    if not obj:
        abort(404, message="Tag not found")

    if not admin and int(obj.user_id) != int(user_id):
        abort(403, message="Access denied.")

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


@blp.route("/<int:tag_id>", methods=["DELETE"])
@jwt_required()
@blp.response(204)
def delete_tag(tag_id):
    user_id = get_identity()
    admin = _is_admin()

    obj = db.session.get(Tag, tag_id)
    if not obj:
        abort(404, message="Tag not found")
    if not admin and int(obj.user_id) != int(user_id):
        abort(403, message="Access denied.")

    db.session.delete(obj)
    db.session.commit()
    return ""
