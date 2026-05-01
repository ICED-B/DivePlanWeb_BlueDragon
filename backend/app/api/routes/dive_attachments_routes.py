# blueprint dive_attachments s prefixem /api/v1/
from flask_smorest import Blueprint, abort
from flask import request
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required, get_jwt

from app.db import db
from app.models.dive_attachment import DiveAttachment
from app.models.dive import Dive
from app.schemas import DiveAttachmentSchema, DiveAttachmentCreateSchema
from app.utils.jwt import get_identity

blp = Blueprint(
    "dive_attachments",
    __name__,
    url_prefix="/api/v1/dive-attachments",
    description="Attachments (files/links)",
)


def _paginate(q):
    page = max(int(request.args.get("page", 1)), 1)
    size = min(max(int(request.args.get("page_size", 50)), 1), 500)
    items = q.limit(size).offset((page - 1) * size).all()
    return items, {"count": q.count(), "page": page, "page_size": size}


def _is_admin() -> bool:
    claims = get_jwt()
    return (claims.get("role") or "").lower() == "admin"


def _check_dive_owner(dive_id: int, user_id: int, admin: bool): # overi zda ponor patri uzivateli jinak 403/404
    if admin:
        return
    dive = db.session.get(Dive, dive_id)
    if not dive:
        abort(404, message="Dive not found")
    if int(dive.user_id) != int(user_id):
        abort(403, message="Access denied.")


@blp.route("/")
@jwt_required()
@blp.response(200, DiveAttachmentSchema(many=True))
def list_attachments():
    user_id = get_identity()
    admin = _is_admin()
    q = db.session.query(DiveAttachment)

    # filtrovani a overeni vlastnictvi pri zadanem dive_id
    if dive_id := request.args.get("dive_id"):
        dive_id = int(dive_id)
        q = q.filter(DiveAttachment.dive_id == dive_id)
        if not admin:
            _check_dive_owner(dive_id, user_id, admin)
    else:
        if not admin:
            q = (
                q.join(Dive, Dive.dive_id == DiveAttachment.dive_id)
                 .filter(Dive.user_id == user_id)
            )
    q = q.order_by(DiveAttachment.created_at.desc())
    items, meta = _paginate(q)
    return items, 200, {"X-Total-Count": str(meta["count"])}


@blp.route("/", methods=["POST"])
@jwt_required()
@blp.arguments(DiveAttachmentCreateSchema)
@blp.response(201, DiveAttachmentSchema)
def create_attachment(payload):
    user_id = int(get_identity())
    admin = _is_admin()

    # payload je DiveAttachment instance (load_instance=True)
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


@blp.route("/<int:attachment_id>", methods=["DELETE"])
@jwt_required()
@blp.response(204)
def delete_attachment(attachment_id):
    user_id = get_identity()
    admin = _is_admin()
    obj = db.session.get(DiveAttachment, attachment_id)
    if not obj:
        abort(404, message="DiveAttachment not found")
    _check_dive_owner(int(obj.dive_id), user_id, admin)
    db.session.delete(obj)
    db.session.commit()
    return ""
