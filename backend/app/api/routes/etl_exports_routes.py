# blueprint etl_exports
from flask_smorest import Blueprint, abort
from flask import request
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required, get_jwt

from app.db import db
from app.models.etl_export import EtlExport
from app.schemas import EtlExportSchema, EtlExportCreateSchema
from app.utils.jwt import get_identity

blp = Blueprint(
    "etl_exports",
    __name__,
    url_prefix="/api/v1/etl-exports",
    description="ETL exports log",
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
@blp.response(200, EtlExportSchema(many=True))
def list_exports():
    user_id = get_identity()
    admin = _is_admin()
    q = db.session.query(EtlExport).order_by(EtlExport.created_at.desc())
    # volitelny filtr podle uzivatele uzivatel muze filtrovat jen sebe
    uid = request.args.get("user_id")
    if uid:
        uid = int(uid)
        if not admin and uid != int(user_id):
            abort(403, message="Access denied.")
        q = q.filter(EtlExport.user_id == uid)
    else:
        if not admin:
            q = q.filter(EtlExport.user_id == user_id)

    items, meta = _paginate(q)
    return items, 200, {"X-Total-Count": str(meta["count"])}


@blp.route("/", methods=["POST"])
@jwt_required()
@blp.arguments(EtlExportCreateSchema)
@blp.response(201, EtlExportSchema)
def create_export(payload):
    user_id = get_identity()
    # user_id nastavuje server, nelze ho zadat v payloadu
    payload["user_id"] = user_id
    obj = EtlExport(**payload)
    db.session.add(obj)
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        abort(400, message=str(e.orig))
    return obj


@blp.route("/<int:export_id>")
@jwt_required()
@blp.response(200, EtlExportSchema)
def get_export(export_id):
    user_id = get_identity()
    admin = _is_admin()
    obj = db.session.get(EtlExport, export_id)
    if not obj:
        abort(404, message="EtlExport not found")
    # kontrola vlastnictvi uzivatel vidi jen svuj zaznam
    if not admin and int(obj.user_id) != int(user_id):
        abort(403, message="Access denied.")
    return obj
