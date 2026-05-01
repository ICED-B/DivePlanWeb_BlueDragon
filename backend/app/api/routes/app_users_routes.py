# blueprint app_users, endpointy pro CRUD
from flask_smorest import Blueprint, abort
from flask import request
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required, get_jwt

from app.db import db
from app.models.app_user import AppUser
from app.schemas import AppUserSchema, AppUserCreateSchema, AppUserUpdateSchema, AppUserMeSchema
from app.utils.jwt import get_identity
from app.utils.password import hash_password, validate_password_strength
from app.services.audit_events import audit_profile_update, audit_delete_account


blp = Blueprint(
    "app_users",
    __name__,
    url_prefix="/api/v1/app-users",
    description="Application users (admin/user)",
)


def _paginate(q):
    page = max(int(request.args.get("page", 1)), 1)
    size = min(max(int(request.args.get("page_size", 50)), 1), 200) # strankovani page page_size, max 200
    items = q.limit(size).offset((page - 1) * size).all()
    return items, {"count": q.count(), "page": page, "page_size": size}


def _is_admin() -> bool:
    claims = get_jwt()      # kontola zda ma uzivatel roli admin z JWT claims
    return (claims.get("role") or "").lower() == "admin"


@blp.route("/")
@jwt_required()
@blp.response(200, AppUserSchema(many=True))
def list_users():
    if not _is_admin():   # vypise list vsech jen adminovi
        abort(403, message="Only admin can list users.")
    q = db.session.query(AppUser).order_by(AppUser.login.asc())
    items, meta = _paginate(q)
    return items, 200, {"X-Total-Count": str(meta["count"])}


@blp.route("/me", methods=["GET"])
@jwt_required()
def get_me():
    user_id = get_identity()    # vrati profil prihlaseneho uzivatele
    obj = db.session.get(AppUser, user_id)
    if not obj:
        abort(404, message="Current user not found")

    if _is_admin():
        return AppUserSchema().dump(obj), 200
    else:
        return AppUserMeSchema().dump(obj), 200


@blp.route("/me", methods=["PATCH"])
@jwt_required()
@blp.arguments(AppUserUpdateSchema)
@blp.response(200, AppUserSchema)
def update_me(payload):
    user_id = get_identity()    # aktualizace profilu, uzivatel muze menit jen povolene dat
    admin = _is_admin()
    raw = request.get_json(silent=True) or {}
    raw_keys = set(raw.keys())

    obj = db.session.get(AppUser, user_id)
    if not obj:
        abort(404, message="Current user not found")

    before = {
        "login": obj.login,
        "first_name": obj.first_name,
        "last_name": obj.last_name,
        "phone": obj.phone,
        "email": obj.email,
        "role": obj.role,
        "is_active": obj.is_active,
    }

    allowed_user_fields = {"login", "first_name", "last_name", "phone", "email"}     # povolená pole pro usera

    raw_password = raw.get("password") if "password" in raw_keys else None  # pouze pro admina
    payload.pop("password", None)  # jen aby se to dál neaplikovalo setatrem

    if raw_password:
        if not admin:
            abort(403, message="Password change is not allowed here.")
        ok, msg = validate_password_strength(raw_password)
        if not ok:
            abort(400, message=msg)
        obj.password_hash = hash_password(raw_password)

    # aplikace zmen: jen pole, ktera opravdu prisla v JSON tele pozadavku
    for k, v in payload.items():
        # "partial update" bez partial=True: aplikuj jen to, co bylo v request JSON
        if k not in raw_keys:
            continue
        if not admin:
            if k not in allowed_user_fields:
                continue
        setattr(obj, k, v)

    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        abort(400, message=str(e.orig))

    after = {
        "login": obj.login,
        "first_name": obj.first_name,
        "last_name": obj.last_name,
        "phone": obj.phone,
        "email": obj.email,
        "role": obj.role,
        "is_active": obj.is_active,
    }

    audit_profile_update(user_id=obj.user_id, before=before, after=after)    # audit (user profil update)

    return obj


@blp.route("/me", methods=["DELETE"])
@jwt_required()
@blp.response(204)
def delete_me():
    user_id = get_identity()        # soft delete 
    obj = db.session.get(AppUser, user_id)
    if not obj:
        abort(404, message="Current user not found")

    # SOFT DELETE
    obj.is_active = False
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        abort(400, message=str(e.orig))
    audit_delete_account(user_id=obj.user_id)
    return ""


@blp.route("/", methods=["POST"])
@jwt_required()
@blp.arguments(AppUserCreateSchema)
@blp.response(201, AppUserSchema)
def create_user(payload):
    # jen admin muze zakladat nove uzivatele zde
    if not _is_admin():
        abort(403, message="Only admin can create users.")
    raw_password = payload.pop("password", None)
    if not raw_password:
        abort(400, message="password is required")

    ok, msg = validate_password_strength(raw_password)
    if not ok:
        abort(400, message=msg)

    payload["password_hash"] = hash_password(raw_password)

    obj = AppUser(**payload)
    db.session.add(obj)
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        abort(400, message=str(e.orig))
    return obj


@blp.route("/<int:user_id>")
@jwt_required()
def get_user(user_id):
    current_id = int(get_identity())    # vrati detail uzivatele podle ID
    admin = _is_admin()

    obj = db.session.get(AppUser, user_id)
    if not obj:
        abort(404, message="AppUser not found")

    # user může vidět jen sebe
    if not admin and current_id != int(user_id):
        abort(403, message="Forbidden")

    if admin:
        return AppUserSchema().dump(obj), 200
    return AppUserMeSchema().dump(obj), 200


@blp.route("/<int:user_id>", methods=["PATCH"])
@jwt_required()
@blp.arguments(AppUserUpdateSchema)
@blp.response(200, AppUserSchema)
def update_user(payload, user_id):
    current_id = int(get_identity())
    admin = _is_admin()
    raw = request.get_json(silent=True) or {}
    raw_keys = set(raw.keys())

    obj = db.session.get(AppUser, user_id)
    if not obj:
        abort(404, message="AppUser not found")

    # user může upravit jen sebe, admin všechny
    if not admin and current_id != int(user_id):
        abort(403, message="Forbidden")

    before = {
        "login": obj.login,
        "first_name": obj.first_name,
        "last_name": obj.last_name,
        "phone": obj.phone,
        "email": obj.email,
        "role": obj.role,
        "is_active": obj.is_active,
    }

    allowed_user_fields = {"login", "first_name",
                           "last_name", "phone", "email"}

    raw_password = raw.get("password") if "password" in raw_keys else None
    payload.pop("password", None)

    if raw_password:
        if not admin:
            abort(403, message="Password change is not allowed here.")
        ok, msg = validate_password_strength(raw_password)
        if not ok:
            abort(400, message=msg)
        obj.password_hash = hash_password(raw_password)

    for k, v in payload.items():
        if k not in raw_keys:
            continue
        if not admin:
            if k not in allowed_user_fields:
                continue
        setattr(obj, k, v)

    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        abort(400, message=str(e.orig))

    after = {
        "login": obj.login,
        "first_name": obj.first_name,
        "last_name": obj.last_name,
        "phone": obj.phone,
        "email": obj.email,
        "role": obj.role,
        "is_active": obj.is_active,
    }

    # audit i pro update přes ID (ať se nezapisuje jen /me)
    audit_profile_update(user_id=obj.user_id, before=before, after=after)

    return obj


@blp.route("/<int:user_id>", methods=["DELETE"])
@jwt_required()
@blp.response(204)
def delete_user(user_id):
    # mazat muze jen admin
    if not _is_admin():
        abort(403, message="Only admin can delete users / deactivate.")

    obj = db.session.get(AppUser, user_id)
    if not obj:
        abort(404, message="AppUser not found")
    # SOFT DELETE
    obj.is_active = False
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        abort(400, message=str(e.orig))
    # audit až po úspěšném commitu
    audit_delete_account(user_id=obj.user_id)
    return ""
