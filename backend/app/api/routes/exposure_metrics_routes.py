# blueprint exposure_metrics
from flask_smorest import Blueprint, abort
from flask import request
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required, get_jwt

from app.db import db
from app.models.exposure_metrics import ExposureMetrics
from app.models.dive import Dive
from app.schemas import (
    ExposureMetricsSchema,
    ExposureMetricsCreateSchema,
    ExposureMetricsUpdateSchema,
)
from app.utils.jwt import get_identity

blp = Blueprint(
    "exposure_metrics",
    __name__,
    url_prefix="/api/v1/exposure-metrics",
    description="O2 exposure (CNS/OTU)",
)


def _paginate(query):
    page = max(int(request.args.get("page", 1)), 1)
    page_size = min(max(int(request.args.get("page_size", 50)), 1), 500)
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
@blp.response(200, ExposureMetricsSchema(many=True))
def list_exposures():
    user_id = get_identity()
    admin = _is_admin()

    q = db.session.query(ExposureMetrics)

    if dive_id := request.args.get("dive_id"):
        dive_id = int(dive_id)
        q = q.filter(ExposureMetrics.dive_id == dive_id)
        if not admin:
            _check_dive_owner(dive_id, user_id, admin)
    else:
        # bez dive_id → omezíme na ponory uživatele
        if not admin:
            q = q.join(Dive, Dive.dive_id == ExposureMetrics.dive_id).filter(
                Dive.user_id == user_id)

    q = q.order_by(ExposureMetrics.dive_id.asc())
    items, meta = _paginate(q)
    return items, 200, {"X-Total-Count": str(meta["count"])}


@blp.route("/", methods=["POST"])
@jwt_required()
@blp.arguments(ExposureMetricsCreateSchema)
@blp.response(201, ExposureMetricsSchema)
def create_exposure(payload):
    user_id = int(get_identity())
    admin = _is_admin()

    # payload je ORM instance (load_instance=True)
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


@blp.route("/<int:exposure_id>")
@jwt_required()
@blp.response(200, ExposureMetricsSchema)
def get_exposure(exposure_id):
    user_id = get_identity()
    admin = _is_admin()

    obj = db.session.get(ExposureMetrics, exposure_id)
    if not obj:
        abort(404, message="ExposureMetrics not found")
    _check_dive_owner(int(obj.dive_id), user_id, admin)
    return obj


@blp.route("/<int:exposure_id>", methods=["PATCH"])
@jwt_required()
@blp.arguments(ExposureMetricsUpdateSchema)
@blp.response(200, ExposureMetricsSchema)
def update_exposure(payload, exposure_id):
    user_id = get_identity()
    admin = _is_admin()

    obj = db.session.get(ExposureMetrics, exposure_id)
    if not obj:
        abort(404, message="ExposureMetrics not found")

    _check_dive_owner(int(obj.dive_id), user_id, admin)
    for k, v in payload.items():
        setattr(obj, k, v)
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        abort(400, message=str(e.orig))
    return obj


@blp.route("/<int:exposure_id>", methods=["DELETE"])
@jwt_required()
@blp.response(204)
def delete_exposure(exposure_id):
    user_id = get_identity()
    admin = _is_admin()

    obj = db.session.get(ExposureMetrics, exposure_id)
    if not obj:
        abort(404, message="ExposureMetrics not found")

    _check_dive_owner(int(obj.dive_id), user_id, admin)
    db.session.delete(obj)
    db.session.commit()
    return ""
