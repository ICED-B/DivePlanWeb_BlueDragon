# blueprint dive_tags
from flask_smorest import Blueprint, abort
from flask import request
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required, get_jwt

from app.db import db
from app.models.dive_tag import DiveTag
from app.models.dive import Dive
from app.schemas import DiveTagSchema, DiveTagCreateSchema
from app.utils.jwt import get_identity

blp = Blueprint(
    "dive_tags",
    __name__,
    url_prefix="/api/v1/dive-tags",
    description="Dive ↔ Tag mapping",
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


@blp.route("/")
@jwt_required()
@blp.response(200, DiveTagSchema(many=True))
def list_dive_tags():
    user_id = get_identity()
    admin = _is_admin()
    q = db.session.query(DiveTag)
    if dive_id := request.args.get("dive_id"):
        dive_id = int(dive_id)
        q = q.filter(DiveTag.dive_id == dive_id)
        if not admin:
            _check_dive_owner(dive_id, user_id, admin)
    else:
        if not admin:
            q = (
                q.join(Dive, Dive.dive_id == DiveTag.dive_id)
                 .filter(Dive.user_id == user_id)
            )

    if tag_id := request.args.get("tag_id"):
        q = q.filter(DiveTag.tag_id == int(tag_id))
    q = q.order_by(DiveTag.dive_id.asc(), DiveTag.tag_id.asc())
    items, meta = _paginate(q)
    return items, 200, {"X-Total-Count": str(meta["count"])}


@blp.route("/", methods=["POST"])
@jwt_required()
@blp.arguments(DiveTagCreateSchema)
@blp.response(201, DiveTagSchema)
def create_dive_tag(payload):
    from app.models.tag import Tag
    user_id = int(get_identity())
    admin = _is_admin()
    dive_id = getattr(payload, "dive_id", None)
    tag_id = getattr(payload, "tag_id", None)

    if not dive_id:
        abort(400, message="dive_id is required")
    if not tag_id:
        abort(400, message="tag_id is required")

    _check_dive_owner(int(dive_id), user_id, admin)

    tag = db.session.get(Tag, int(tag_id))
    if not tag:
        abort(404, message="Tag not found")
    if not admin and int(tag.user_id) != user_id:
        abort(403, message="Tag does not belong to this user.")

    db.session.add(payload)
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        abort(400, message=str(e.orig))
    return payload


@blp.route("/<int:dive_id>/<int:tag_id>", methods=["DELETE"])
@jwt_required()
@blp.response(204)
def delete_dive_tag(dive_id, tag_id):
    user_id = get_identity()
    admin = _is_admin()
    obj = db.session.query(DiveTag).get((dive_id, tag_id))
    if not obj:
        abort(404, message="DiveTag not found")

    _check_dive_owner(int(dive_id), user_id, admin)
    db.session.delete(obj)
    db.session.commit()
    return ""
