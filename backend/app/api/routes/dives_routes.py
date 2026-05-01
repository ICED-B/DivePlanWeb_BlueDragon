# blueprint dives
from __future__ import annotations
import io
from flask_smorest import Blueprint, abort
from flask import request, send_file, make_response
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required, get_jwt

from app.db import db
from app.models.dive import Dive
from app.schemas import DiveSchema, DiveCreateSchema, DiveUpdateSchema, DiveDetailSchema
from app.utils.jwt import get_identity
from app.services.export_service import export_dives_uddf, ExportServiceError
from app.planner.core.deco_tables import plan_dive
from app.planner.core.types import PlannerServiceError
from app.models.trip import Trip
from app.models.device import Device
from app.models.site import Site
from app.models.license import License


blp = Blueprint(
    "dives",
    __name__,
    url_prefix="/api/v1/dives",
    description="Dives CRUD & export & planning",
)


def _paginate(query):
    page = max(int(request.args.get("page", 1)), 1)
    page_size = min(max(int(request.args.get("page_size", 20)), 1), 200)
    items = query.limit(page_size).offset((page - 1) * page_size).all()
    return items, {"page": page, "page_size": page_size, "count": query.count()}


def _is_admin() -> bool:
    claims = get_jwt()
    return (claims.get("role") or "").lower() == "admin"


def _apply_owner_filter(query, user_id: int, admin: bool):
    if admin:
        return query
    return query.filter(Dive.user_id == user_id)


def _check_dive_owner(dive: Dive, user_id: int, admin: bool):
    if admin:
        return
    if int(dive.user_id) != int(user_id):
        abort(403, message="Access denied.")


def _check_fk_owner(model_cls, obj_id, user_id: int, admin: bool, label: str):
    if admin or obj_id is None:
        return
    obj = db.session.get(model_cls, int(obj_id))
    if not obj:
        abort(404, message=f"{label} not found")
    if int(getattr(obj, "user_id")) != int(user_id):
        abort(403, message=f"{label} does not belong to this user.")


@blp.route("/")
@jwt_required()
@blp.response(200, DiveSchema(many=True))
def list_dives():
    user_id = get_identity()
    admin = _is_admin()

    q = db.session.query(Dive).order_by(Dive.start_time.desc())
    q = _apply_owner_filter(q, user_id, admin)
    items, meta = _paginate(q)
    return items, 200, {"X-Total-Count": str(meta["count"])}


@blp.route("/", methods=["POST"])
@jwt_required()
@blp.arguments(DiveCreateSchema)
@blp.response(201, DiveSchema)
def create_dive(payload):
    user_id = get_identity()
    admin = _is_admin()
    payload["user_id"] = user_id

    _check_fk_owner(Trip, payload.get("trip_id"), user_id, admin, "Trip")
    _check_fk_owner(Device, payload.get("device_id"), user_id, admin, "Device")
    _check_fk_owner(Site, payload.get("site_id"), user_id, admin, "Site")
    _check_fk_owner(License, payload.get(
        "license_id"), user_id, admin, "License")

    dive = Dive(**payload)
    db.session.add(dive)
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        abort(400, message=str(e.orig))
    return dive


@blp.route("/<int:dive_id>")
@jwt_required()
@blp.response(200, DiveSchema)
def get_dive(dive_id):
    user_id = get_identity()
    admin = _is_admin()
    dive = db.session.get(Dive, dive_id)
    if not dive:
        abort(404, message="Dive not found")
    _check_dive_owner(dive, user_id, admin)
    return dive


@blp.route("/<int:dive_id>", methods=["PATCH"])
@jwt_required()
@blp.arguments(DiveUpdateSchema)
@blp.response(200, DiveSchema)
def update_dive(payload, dive_id):
    user_id = get_identity()
    admin = _is_admin()

    dive = db.session.get(Dive, dive_id)
    if not dive:
        abort(404, message="Dive not found")
    _check_dive_owner(dive, user_id, admin)
    # ověř jen ty FK, které se mění (ať to neblokuje update bez FK)
    if "trip_id" in payload:
        _check_fk_owner(Trip, payload.get("trip_id"), user_id, admin, "Trip")
    if "device_id" in payload:
        _check_fk_owner(Device, payload.get(
            "device_id"), user_id, admin, "Device")
    if "site_id" in payload:
        _check_fk_owner(Site, payload.get("site_id"), user_id, admin, "Site")
    if "license_id" in payload:
        _check_fk_owner(License, payload.get(
            "license_id"), user_id, admin, "License")

    # owner se nemění z payloadu
    payload.pop("user_id", None)
    for k, v in payload.items():
        setattr(dive, k, v)
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        abort(400, message=str(e.orig))
    return dive


@blp.route("/<int:dive_id>", methods=["DELETE"])
@jwt_required()
@blp.response(204)
def delete_dive(dive_id):
    user_id = get_identity()
    admin = _is_admin()
    dive = db.session.get(Dive, dive_id)
    if not dive:
        abort(404, message="Dive not found")
    _check_dive_owner(dive, user_id, admin)
    db.session.delete(dive)
    db.session.commit()
    return ""


@blp.route("/<int:dive_id>/detail")
@jwt_required()
@blp.response(200, DiveDetailSchema)
def get_dive_detail(dive_id):
    user_id = get_identity()
    admin = _is_admin()
    dive = db.session.get(Dive, dive_id)
    if not dive:
        abort(404, message="Dive not found")
    _check_dive_owner(dive, user_id, admin)
    return dive


@blp.route("/<int:dive_id>/export/uddf")
@jwt_required()
def export_uddf(dive_id):
    user_id = get_identity()
    admin = _is_admin()
    dive = db.session.get(Dive, dive_id)
    if not dive:
        abort(404, message="Dive not found")
    _check_dive_owner(dive, user_id, admin)

    try:
        # admin muze exportovat cizi ponor - user_id v service vynecháme
        xml_data = export_dives_uddf(
            dive_ids=[dive_id], user_id=None if admin else user_id)
    except ExportServiceError as e:
        abort(400, message=str(e))

    return send_file(
        io.BytesIO(xml_data.encode("utf-8")),
        mimetype="application/xml",
        as_attachment=True,
        download_name=f"dive_{dive_id}.uddf.xml",
    )


@blp.route("/<int:dive_id>/plan")
@jwt_required()
def plan_dive_from_record(dive_id):
    user_id = get_identity()
    admin = _is_admin()
    dive = db.session.get(Dive, dive_id)
    if not dive:
        abort(404, message="Dive not found")

    _check_dive_owner(dive, user_id, admin)

    depth_m = getattr(dive, "max_depth_m", None) or getattr(
        dive, "max_depth", None) or getattr(dive, "depth", None)
    if depth_m is None:
        abort(400, message="Dive nemá uloženou hloubku.")

    bottom_time = getattr(dive, "duration_min", None) or getattr(
        dive, "duration", None)
    if bottom_time is None:
        abort(400, message="Dive nemá uložený čas/duration.")

    f_o2 = None
    try:
        # FO2 zkusime z prvniho segmentu
        if getattr(dive, "segments", None):
            seg0 = dive.segments[0]
        if seg0 and getattr(seg0, "gas_mix", None) and hasattr(seg0.gas_mix, "o2_percent"):
            f_o2 = float(seg0.gas_mix.o2_percent) / 100.0

        # fallback z prvniho tanku
        if f_o2 is None and getattr(dive, "tanks", None):
            t0 = dive.tanks[0]
        if t0 and getattr(t0, "gas_mix", None) and hasattr(t0.gas_mix, "o2_percent"):
            f_o2 = float(t0.gas_mix.o2_percent) / 100.0
    except Exception:
        f_o2 = None

    try:
        plan = plan_dive(depth_m=float(depth_m),
                         bottom_time_min=float(bottom_time), f_o2=f_o2)
    except PlannerServiceError as e:
        abort(400, message=str(e))
    return plan
