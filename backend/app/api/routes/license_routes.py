# blueprint licenses
from flask_smorest import Blueprint, abort
from flask import request
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required, get_jwt

from app.db import db
from app.models.license import License
from app.schemas import LicenseSchema, LicenseCreateSchema, LicenseUpdateSchema
from app.utils.jwt import get_identity

blp = Blueprint(
    "licenses",
    __name__,
    url_prefix="/api/v1/licenses",
    description="Licenses (evidence of certifications) per user",
)


def _paginate(query):
    page = max(int(request.args.get("page", 1)), 1)
    page_size = min(max(int(request.args.get("page_size", 50)), 1), 200)
    items = query.limit(page_size).offset((page - 1) * page_size).all()
    return items, {"page": page, "page_size": page_size, "count": query.count()}


def _is_admin() -> bool:
    claims = get_jwt()
    return (claims.get("role") or "").lower() == "admin"


@blp.route("/")
@jwt_required()
@blp.response(200, LicenseSchema(many=True))
def list_licenses():
    current_user_id = get_identity()
    admin = _is_admin()

    q = db.session.query(License)

    # admin muze filtrovat podle konkretniho uzivatele
    uid = request.args.get("user_id")
    if uid:
        uid = int(uid)
        if not admin and uid != int(current_user_id):
            abort(403, message="Access denied.")
        q = q.filter(License.user_id == uid)
    else:
        if not admin:
            q = q.filter(License.user_id == current_user_id)
    q = q.order_by(License.license_id.desc())
    items, meta = _paginate(q)
    return items, 200, {"X-Total-Count": str(meta["count"])}


@blp.route("/", methods=["POST"])
@jwt_required()
@blp.arguments(LicenseCreateSchema)
@blp.response(201, LicenseSchema)
def create_license(payload):
    current_user_id = get_identity()
    # payload je License instance (load_instance=True), user_id nastavuje server
    payload.user_id = int(current_user_id)

    db.session.add(payload)
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        abort(400, message=str(e.orig))

    return payload


@blp.route("/<int:license_id>")
@jwt_required()
@blp.response(200, LicenseSchema)
def get_license(license_id):
    current_user_id = get_identity()
    admin = _is_admin()

    obj = db.session.get(License, license_id)
    if not obj:
        abort(404, message="License not found")

    if not admin and int(obj.user_id) != int(current_user_id):
        abort(403, message="Access denied.")
    return obj


@blp.route("/<int:license_id>", methods=["PATCH"])
@jwt_required()
@blp.arguments(LicenseUpdateSchema)
@blp.response(200, LicenseSchema)
def update_license(payload, license_id):
    current_user_id = get_identity()
    admin = _is_admin()

    obj = db.session.get(License, license_id)
    if not obj:
        abort(404, message="License not found")

    if not admin and int(obj.user_id) != int(current_user_id):
        abort(403, message="Access denied.")

    # user_id nikdy neměníme z payloadu
    for k, v in payload.items():
        if k == "user_id":
            continue
        setattr(obj, k, v)

    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        abort(400, message=str(e.orig))
    return obj


@blp.route("/<int:license_id>", methods=["DELETE"])
@jwt_required()
@blp.response(204)
def delete_license(license_id):
    current_user_id = get_identity()
    admin = _is_admin()

    obj = db.session.get(License, license_id)
    if not obj:
        abort(404, message="License not found")

    if not admin and int(obj.user_id) != int(current_user_id):
        abort(403, message="Access denied.")
    db.session.delete(obj)
    db.session.commit()
    return ""
