# blueprint sites
from flask_smorest import Blueprint, abort
from flask import request
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required, get_jwt

from app.db import db
from app.models.site import Site
from app.schemas import SiteSchema, SiteCreateSchema, SiteUpdateSchema
from app.utils.jwt import get_identity

blp = Blueprint(
    "sites",
    __name__,
    url_prefix="/api/v1/sites",
    description="Dive sites (user-owned)",
)


def _paginate(query):
    page = max(int(request.args.get("page", 1)), 1)
    page_size = min(max(int(request.args.get("page_size", 50)), 1), 200)
    items = query.limit(page_size).offset((page - 1) * page_size).all()
    return items, {"page": page, "page_size": page_size, "count": query.count()}


def _is_admin() -> bool:
    claims = get_jwt()
    return (claims.get("role") or "").lower() == "admin"


def _can_access(site: Site, user_id: int) -> bool:
    return _is_admin() or int(site.user_id) == int(user_id)


@blp.route("/")
@jwt_required()
@blp.response(200, SiteSchema(many=True))
def list_sites():
    user_id = int(get_identity())

    q = db.session.query(Site)

    # ownership
    if not _is_admin():
        q = q.filter(Site.user_id == user_id)

    # volitelný filtr podle názvu
    if name := request.args.get("q"):
        q = q.filter(Site.name.ilike(f"%{name}%"))

    q = q.order_by(Site.name.asc())

    items, meta = _paginate(q)
    return items, 200, {"X-Total-Count": str(meta["count"])}


@blp.route("/", methods=["POST"])
@jwt_required()
@blp.arguments(SiteCreateSchema)
@blp.response(201, SiteSchema)
def create_site(payload):
    user_id = int(get_identity())

    obj = Site(user_id=user_id, **payload)
    db.session.add(obj)
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        abort(400, message=str(e.orig))
    return obj


@blp.route("/<int:site_id>")
@jwt_required()
@blp.response(200, SiteSchema)
def get_site(site_id):
    user_id = int(get_identity())

    obj = db.session.get(Site, site_id)
    if not obj:
        abort(404, message="Site not found")
    if not _can_access(obj, user_id):
        abort(403, message="Not allowed")
    return obj


@blp.route("/<int:site_id>", methods=["PATCH"])
@jwt_required()
@blp.arguments(SiteUpdateSchema)
@blp.response(200, SiteSchema)
def update_site(payload, site_id):
    user_id = int(get_identity())

    obj = db.session.get(Site, site_id)
    if not obj:
        abort(404, message="Site not found")
    if not _can_access(obj, user_id):
        abort(403, message="Not allowed")

    for k, v in payload.items():
        setattr(obj, k, v)

    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        abort(400, message=str(e.orig))
    return obj


@blp.route("/<int:site_id>", methods=["DELETE"])
@jwt_required()
@blp.response(204)
def delete_site(site_id):
    user_id = int(get_identity())

    obj = db.session.get(Site, site_id)
    if not obj:
        abort(404, message="Site not found")
    if not _can_access(obj, user_id):
        abort(403, message="Not allowed")

    db.session.delete(obj)
    db.session.commit()
    return ""
