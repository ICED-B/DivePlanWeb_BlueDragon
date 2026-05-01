from flask_smorest import Blueprint, abort
from flask import request
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required, get_jwt

from app.db import db
from app.models.token_blacklist import TokenBlacklist
from app.schemas import TokenBlacklistSchema

blp = Blueprint(
    "token_blacklist",
    __name__,
    url_prefix="/api/v1/token-blacklist",
    description="JWT token blacklist",
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
@blp.response(200, TokenBlacklistSchema(many=True))
def list_blacklisted():
    if not _is_admin():
        abort(403, message="Only admin can view blacklisted tokens.")
    q = db.session.query(TokenBlacklist).order_by(
        TokenBlacklist.created_at.desc())
    items, meta = _paginate(q)
    return items, 200, {"X-Total-Count": str(meta["count"])}


@blp.route("/", methods=["POST"])
@jwt_required()
@blp.arguments(TokenBlacklistSchema)
@blp.response(201, TokenBlacklistSchema)
def blacklist_token(payload):
    if not _is_admin():
        abort(403, message="Only admin can blacklist tokens.")
    obj = TokenBlacklist(**payload)
    db.session.add(obj)
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        abort(400, message=str(e.orig))
    return obj


@blp.route("/<int:item_id>")
@jwt_required()
@blp.response(200, TokenBlacklistSchema)
def get_blacklisted(item_id):
    if not _is_admin():
        abort(403, message="Only admin can view blacklisted tokens.")
    obj = db.session.get(TokenBlacklist, item_id)
    if not obj:
        abort(404, message="Blacklisted token not found")
    return obj
