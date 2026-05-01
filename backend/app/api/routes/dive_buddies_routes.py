# blueprint dive_buddies s prefixem /api/v1/
from flask_smorest import Blueprint, abort
from flask import request
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required, get_jwt

from app.db import db
from app.models.dive_buddy import DiveBuddy
from app.models.dive import Dive
from app.models.buddy import Buddy
from app.schemas import DiveBuddySchema, DiveBuddyCreateSchema, DiveBuddyUpdateSchema
from app.utils.jwt import get_identity

blp = Blueprint(
    "dive_buddies",
    __name__,
    url_prefix="/api/v1/dive-buddies",
    description="Dive ↔ Buddy mapping",
)


def _paginate(q):
    page = max(int(request.args.get("page", 1)), 1)
    size = min(max(int(request.args.get("page_size", 50)), 1), 500) # strankovani
    items = q.limit(size).offset((page - 1) * size).all()
    return items, {"count": q.count(), "page": page, "page_size": size}


def _is_admin() -> bool:
    claims = get_jwt()
    return (claims.get("role") or "").lower() == "admin"    # check role


def _check_dive_owner(dive_id: int, user_id: int, admin: bool): # check vlastnictvi
    if admin:
        return
    dive = db.session.get(Dive, dive_id)
    if not dive:
        abort(404, message="Dive not found")
    if int(dive.user_id) != int(user_id):
        abort(403, message="Access denied.")


@blp.route("/")
@jwt_required()
@blp.response(200, DiveBuddySchema(many=True))
def list_dive_buddies():
    user_id = get_identity()
    admin = _is_admin()
    q = db.session.query(DiveBuddy)
    dive_id = request.args.get("dive_id")
    buddy_id = request.args.get("buddy_id")

    if dive_id:
        dive_id_int = int(dive_id)
        q = q.filter(DiveBuddy.dive_id == dive_id_int)
        if not admin:
            _check_dive_owner(dive_id_int, user_id, admin)
    else:
        if not admin:
            q = (
                q.join(Dive, Dive.dive_id == DiveBuddy.dive_id)
                 .filter(Dive.user_id == user_id)
            )
    if buddy_id:
        q = q.filter(DiveBuddy.buddy_id == int(buddy_id))
    q = q.order_by(DiveBuddy.dive_id.desc(), DiveBuddy.buddy_id.asc())
    items, meta = _paginate(q)
    return items, 200, {"X-Total-Count": str(meta["count"])}


@blp.route("/", methods=["POST"])
@jwt_required()
@blp.arguments(DiveBuddyCreateSchema)
@blp.response(201, DiveBuddySchema)
def create_dive_buddy(payload):
    user_id = int(get_identity())
    admin = _is_admin()
    # payload je DiveBuddy instance (load_instance=True)
    dive_id = getattr(payload, "dive_id", None)
    buddy_id = getattr(payload, "buddy_id", None)

    if not dive_id or not buddy_id:
        abort(400, message="dive_id and buddy_id are required")
    _check_dive_owner(int(dive_id), user_id, admin)

    buddy = db.session.get(Buddy, int(buddy_id))
    if not buddy:
        abort(404, message="Buddy not found")
    if not admin and int(buddy.user_id) != user_id:
        abort(403, message="Buddy does not belong to this user.")
        
    db.session.add(payload)
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        abort(400, message=str(e.orig))
    return payload


@blp.route("/<int:dive_id>/<int:buddy_id>", methods=["PATCH"])
@jwt_required()
@blp.arguments(DiveBuddyUpdateSchema)
@blp.response(200, DiveBuddySchema)
def update_dive_buddy(payload, dive_id: int, buddy_id: int):
    user_id = get_identity()
    admin = _is_admin()

    _check_dive_owner(int(dive_id), user_id, admin)
    buddy = db.session.get(Buddy, int(buddy_id))
    if not buddy:
        abort(404, message="Buddy not found")
    if not admin and int(buddy.user_id) != int(user_id):
        abort(403, message="Buddy does not belong to this user.")

    obj = (
        db.session.query(DiveBuddy)
        .filter(DiveBuddy.dive_id == dive_id, DiveBuddy.buddy_id == buddy_id)
        .first()
    )
    if not obj:
        abort(404, message="DiveBuddy not found")

    for k, v in payload.items():
        setattr(obj, k, v)

    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        abort(400, message=str(e.orig))
    return obj


@blp.route("/<int:dive_id>/<int:buddy_id>", methods=["DELETE"])
@jwt_required()
@blp.response(204)
def delete_dive_buddy(dive_id: int, buddy_id: int):
    user_id = get_identity()
    admin = _is_admin()

    _check_dive_owner(int(dive_id), user_id, admin)
    buddy = db.session.get(Buddy, int(buddy_id))
    if not buddy:
        abort(404, message="Buddy not found")
    if not admin and int(buddy.user_id) != int(user_id):
        abort(403, message="Buddy does not belong to this user.")

    obj = (
        db.session.query(DiveBuddy)
        .filter(DiveBuddy.dive_id == dive_id, DiveBuddy.buddy_id == buddy_id)
        .first()
    )
    if not obj:
        abort(404, message="DiveBuddy not found")
    db.session.delete(obj)
    db.session.commit()
    return ""
