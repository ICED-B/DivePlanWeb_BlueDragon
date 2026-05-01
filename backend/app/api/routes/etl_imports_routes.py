# blueprint etl_imports
from flask_smorest import Blueprint, abort
from flask import request
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required, get_jwt

from app.db import db
from app.models.etl_import import EtlImport
from app.schemas import EtlImportSchema, EtlImportCreateSchema
from app.utils.jwt import get_identity

blp = Blueprint(
    "etl_imports",
    __name__,
    url_prefix="/api/v1/etl-imports",
    description="ETL imports log",
)


def _paginate(q):
    page = max(int(request.args.get("page", 1)), 1)
    size = min(max(int(request.args.get("page_size", 50)), 1), 500)
    items = q.limit(size).offset((page - 1) * size).all()
    return items, {"count": q.count(), "page": page, "page_size": size}


def _is_admin() -> bool:
    claims = get_jwt()
    return (claims.get("role") or "").lower() == "admin"


@blp.route("/")
@jwt_required()
@blp.response(200, EtlImportSchema(many=True))
def list_imports():
    user_id = get_identity()
    admin = _is_admin()
    q = db.session.query(EtlImport).order_by(EtlImport.created_at.desc())
    # volitelny filtr podle uzivatele uzivatel muze filtrovat jen sebe
    uid = request.args.get("user_id")
    if uid:
        uid = int(uid)
        if not admin and uid != int(user_id):
            abort(403, message="Access denied.")
        q = q.filter(EtlImport.user_id == uid)
    else:
        if not admin:
            q = q.filter(EtlImport.user_id == user_id)
    items, meta = _paginate(q)
    return items, 200, {"X-Total-Count": str(meta["count"])}


@blp.route("/", methods=["POST"])
@jwt_required()
@blp.arguments(EtlImportCreateSchema)
@blp.response(201, EtlImportSchema)
def create_import(payload):
    user_id = get_identity()
    # user_id nastavuje server, nelze ho zadat v payloadu
    payload["user_id"] = user_id
    obj = EtlImport(**payload)
    db.session.add(obj)
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        abort(400, message=str(e.orig))
    return obj


@blp.route("/<int:import_id>")
@jwt_required()
@blp.response(200, EtlImportSchema)
def get_import(import_id):
    user_id = get_identity()
    admin = _is_admin()
    obj = db.session.get(EtlImport, import_id)
    if not obj:
        abort(404, message="EtlImport not found")

    # kontrola vlastnictvi uzivatel vidi jen svuj zaznam
    if not admin and int(obj.user_id) != int(user_id):
        abort(403, message="Access denied.")
    return obj
