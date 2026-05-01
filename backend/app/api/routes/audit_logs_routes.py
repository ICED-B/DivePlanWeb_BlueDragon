# blueprint audit_logs, pouze pro admina
from flask_smorest import Blueprint, abort
from flask import request
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required, get_jwt

from app.db import db
from app.models.audit_log import AuditLog
from app.schemas import AuditLogSchema
from app.utils.jwt import get_identity


blp = Blueprint(
    "audit_logs",
    __name__,
    url_prefix="/api/v1/audit-logs",
    description="Audit log",
)


def _paginate(q):
    page = max(int(request.args.get("page", 1)), 1)
    size = min(max(int(request.args.get("page_size", 100)), 1), 1000)   # strankovani page a page_size max 1000 na stranku
    items = q.limit(size).offset((page - 1) * size).all()
    return items, {"count": q.count(), "page": page, "page_size": size}


def _is_admin() -> bool:
    claims = get_jwt()      #check role z jwt claim
    return (claims.get("role") or "").lower() == "admin"


@blp.route("/")
@jwt_required()
@blp.response(200, AuditLogSchema(many=True))
def list_audits():
    current_id = get_identity()
    admin = _is_admin()
    if not admin:
        abort(403, message="Only admin can access audit logs.")

    q = db.session.query(AuditLog).order_by(AuditLog.created_at.desc())

    # volitelny filtr podle uzivatele
    uid = request.args.get("user_id")
    if uid:
        uid = int(uid)
        if not admin and uid != int(current_id):
            abort(403, message="Forbidden")
        q = q.filter(AuditLog.user_id == uid)
    else:
        if not admin:
            q = q.filter((AuditLog.user_id == current_id) |
                         (AuditLog.performed_by == current_id))

    items, meta = _paginate(q)
    return items, 200, {"X-Total-Count": str(meta["count"])}


@blp.route("/", methods=["POST"])
@jwt_required()
@blp.arguments(AuditLogSchema)
@blp.response(201, AuditLogSchema)
def create_audit(payload):
    current_id = get_identity()
    if not _is_admin():
        abort(403, message="Only admin can create audit logs.")

    payload["user_id"] = current_id
    payload["performed_by"] = current_id

    obj = AuditLog(**payload)
    db.session.add(obj)
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        abort(400, message=str(e.orig))
    return obj


@blp.route("/<int:audit_id>")
@jwt_required()
@blp.response(200, AuditLogSchema)
def get_audit(audit_id):
    current_id = get_identity()
    admin = _is_admin()
    if not admin:
        abort(403, message="Only admin can access audit logs.")

    obj = db.session.get(AuditLog, audit_id)
    if not obj:
        abort(404, message="AuditLog not found")

    if not admin:
        if obj.user_id != current_id and obj.performed_by != current_id:
            abort(403, message="Forbidden")
    return obj
