# blueprint buddies
from flask_smorest import Blueprint, abort
from flask import request
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required, get_jwt

from app.db import db
from app.models.buddy import Buddy
from app.schemas import BuddySchema, BuddyCreateSchema, BuddyUpdateSchema
from app.utils.jwt import get_identity

blp = Blueprint(
    "buddies",
    __name__,
    url_prefix="/api/v1/buddies",
    description="Dive buddies",
)


def _paginate(q):
    page = max(int(request.args.get("page", 1)), 1)
    size = min(max(int(request.args.get("page_size", 50)), 1), 200) # max 200 zaznamu na stranku
    items = q.limit(size).offset((page - 1) * size).all()
    return items, {"count": q.count(), "page": page, "page_size": size}


def _is_admin() -> bool:
    claims = get_jwt()  # check role admin z jwt claims
    return (claims.get("role") or "").lower() == "admin"


@blp.route("/")
@jwt_required()
@blp.response(200, BuddySchema(many=True))
def list_buddies():
    user_id = get_identity()
    admin = _is_admin()

    q = db.session.query(Buddy).order_by(Buddy.name.asc())
    # bezny uzivatel vidi jen sve partnery
    if not admin:
        q = q.filter(Buddy.user_id == user_id)

    # admin muze filtrovat podle konkretniho uzivatele
    if admin and (uid := request.args.get("user_id")):
        q = q.filter(Buddy.user_id == int(uid))
    items, meta = _paginate(q)
    return items, 200, {"X-Total-Count": str(meta["count"])}


@blp.route("/", methods=["POST"])
@jwt_required()
@blp.arguments(BuddyCreateSchema)
@blp.response(201, BuddySchema)
def create_buddy(payload):
    user_id = int(get_identity())

    # payload je Buddy instance (load_instance=True), user_id se nastavuje ze JWT
    payload.user_id = user_id
    db.session.add(payload)
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        abort(400, message=str(e.orig))
    return payload


@blp.route("/<int:buddy_id>")
@jwt_required()
@blp.response(200, BuddySchema)
def get_buddy(buddy_id):
    user_id = get_identity()
    admin = _is_admin()

    obj = db.session.get(Buddy, buddy_id)
    if not obj:
        abort(404, message="Buddy not found")
    if not admin and int(obj.user_id) != int(user_id):
        abort(403, message="Access denied")
    return obj


@blp.route("/<int:buddy_id>", methods=["PATCH"])
@jwt_required()
@blp.arguments(BuddyUpdateSchema)
@blp.response(200, BuddySchema)
def update_buddy(payload, buddy_id):
    user_id = get_identity()
    admin = _is_admin()

    obj = db.session.get(Buddy, buddy_id)
    if not obj:
        abort(404, message="Buddy not found")
    if not admin and int(obj.user_id) != int(user_id):
        abort(403, message="Access denied")

    payload.pop("user_id", None)
    for k, v in payload.items():
        setattr(obj, k, v)

    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        abort(400, message=str(e.orig))
    return obj


@blp.route("/<int:buddy_id>", methods=["DELETE"])
@jwt_required()
@blp.response(204)
def delete_buddy(buddy_id):
    user_id = get_identity()
    admin = _is_admin()

    obj = db.session.get(Buddy, buddy_id)
    if not obj:
        abort(404, message="Buddy not found")
    if not admin and int(obj.user_id) != int(user_id):
        abort(403, message="Access denied")

    db.session.delete(obj)
    db.session.commit()
    return ""
