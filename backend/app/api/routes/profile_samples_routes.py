# blueprint profile_samples
from flask_smorest import Blueprint, abort
from flask import request
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required, get_jwt

from app.db import db
from app.models.profile_sample import ProfileSample
from app.models.dive import Dive
from app.schemas import (
    ProfileSampleSchema,
    ProfileSampleCreateSchema,
    ProfileSampleUpdateSchema,
)
from app.utils.jwt import get_identity

blp = Blueprint(
    "profile_samples",
    __name__,
    url_prefix="/api/v1/profile-samples",
    description="Samples (time/depth/temp)",
)


def _paginate(query):
    page = max(int(request.args.get("page", 1)), 1)
    page_size = min(max(int(request.args.get("page_size", 500)), 1), 5000)
    items = query.limit(page_size).offset((page - 1) * page_size).all()
    return items, {"count": query.count(), "page": page, "page_size": page_size}


def _is_admin() -> bool:
    claims = get_jwt()
    return (claims.get("role") or "").lower() == "admin"


def _check_dive_owner(dive_id: int, user_id: int, admin: bool):
    if admin:
        return
    dive = db.session.get(Dive, dive_id)
    if not dive:
        abort(404, message="Dive not found")
    if int(dive.user_id) != int(user_id):
        abort(403, message="Access denied.")


@blp.route("/")
@jwt_required()
@blp.response(200, ProfileSampleSchema(many=True))
def list_samples():
    user_id = get_identity()
    admin = _is_admin()

    q = db.session.query(ProfileSample)
    if dive_id := request.args.get("dive_id"):
        dive_id = int(dive_id)
        q = q.filter(ProfileSample.dive_id == dive_id)
        if not admin:
            _check_dive_owner(dive_id, user_id, admin)
    else:
        if not admin:
            # join na Dive zajistuje omezeni na vlastni ponory
            q = q.join(Dive, Dive.dive_id == ProfileSample.dive_id).filter(
                Dive.user_id == user_id
            )

    q = q.order_by(ProfileSample.dive_id.asc(), ProfileSample.t_min.asc())
    items, meta = _paginate(q)
    return items, 200, {"X-Total-Count": str(meta["count"])}


@blp.route("/", methods=["POST"])
@jwt_required()
@blp.arguments(ProfileSampleCreateSchema)
@blp.response(201, ProfileSampleSchema)
def create_sample(payload):
    """Prida novy vzorek profilu k ponoru. Overi vlastnictvi ponoru."""
    user_id = int(get_identity())
    admin = _is_admin()

    # payload je ProfileSample instance (load_instance=True)
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


@blp.route("/<int:sample_id>")
@jwt_required()
@blp.response(200, ProfileSampleSchema)
def get_sample(sample_id):
    user_id = get_identity()
    admin = _is_admin()
    obj = db.session.get(ProfileSample, sample_id)
    if not obj:
        abort(404, message="ProfileSample not found")
    _check_dive_owner(int(obj.dive_id), user_id, admin)
    return obj


@blp.route("/<int:sample_id>", methods=["PATCH"])
@jwt_required()
@blp.arguments(ProfileSampleUpdateSchema)
@blp.response(200, ProfileSampleSchema)
def update_sample(payload, sample_id):
    user_id = get_identity()
    admin = _is_admin()
    obj = db.session.get(ProfileSample, sample_id)
    if not obj:
        abort(404, message="ProfileSample not found")
    _check_dive_owner(int(obj.dive_id), user_id, admin)

    for k, v in payload.items():
        setattr(obj, k, v)
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        abort(400, message=str(e.orig))
    return obj


@blp.route("/<int:sample_id>", methods=["DELETE"])
@jwt_required()
@blp.response(204)
def delete_sample(sample_id):
    user_id = get_identity()
    admin = _is_admin()
    obj = db.session.get(ProfileSample, sample_id)
    if not obj:
        abort(404, message="ProfileSample not found")

    _check_dive_owner(int(obj.dive_id), user_id, admin)
    db.session.delete(obj)
    db.session.commit()
    return ""
