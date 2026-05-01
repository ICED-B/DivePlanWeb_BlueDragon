# blueprint exports
from __future__ import annotations
from flask import request, make_response
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt

from app.services.export_service import (
    export_dives_json,
    export_dives_csv,
    export_dives_uddf,
    ExportServiceError,
)
from app.utils.jwt import get_identity

blp = Blueprint(
    "exports",
    __name__,
    url_prefix="/api/v1/exports",
    description="Export realnych dat (ponory) do JSON/CSV/UDDF",
)


def _is_admin() -> bool:
    claims = get_jwt()
    return (claims.get("role") or "").lower() == "admin"

# Z query param dive_ids=1,2,3 udela list[int], chybejici param None
def _parse_ids(param_name: str = "dive_ids") -> list[int] | None:
    raw = request.args.get(param_name)
    if not raw:
        return None
    ids: list[int] = []
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            ids.append(int(part))
        except ValueError:
            abort(400, message=f"Neplatne ID v parametru {param_name}: {part}")
    return ids or None


def _resolve_user_id():
    current_user_id = get_identity()
    admin = _is_admin()
    param_user_id = request.args.get("user_id")
    if admin and param_user_id:
        try:
            return int(param_user_id)
        except ValueError:
            abort(400, message="user_id musi byt cislo")
    return current_user_id


@blp.route("/dives/json", methods=["GET"])
@jwt_required()
def export_dives_as_json():
    user_id = _resolve_user_id()
    dive_ids = _parse_ids()
    try:
        payload = export_dives_json(dive_ids=dive_ids, user_id=user_id)
    except ExportServiceError as e:
        abort(400, message=str(e))
    resp = make_response(payload, 200)
    resp.headers["Content-Type"] = "application/json; charset=utf-8"
    return resp


@blp.route("/dives/csv", methods=["GET"])
@jwt_required()
def export_dives_as_csv():
    user_id = _resolve_user_id()
    dive_ids = _parse_ids()
    try:
        csv_data = export_dives_csv(dive_ids=dive_ids, user_id=user_id)
    except ExportServiceError as e:
        abort(400, message=str(e))
    resp = make_response(csv_data, 200)
    resp.headers["Content-Type"] = "text/csv; charset=utf-8"
    resp.headers["Content-Disposition"] = "attachment; filename=dives.csv"
    return resp


@blp.route("/dives/uddf", methods=["GET"])
@jwt_required()
def export_dives_as_uddf():
    user_id = _resolve_user_id()
    dive_ids = _parse_ids()
    try:
        xml_data = export_dives_uddf(dive_ids=dive_ids, user_id=user_id)
    except ExportServiceError as e:
        abort(400, message=str(e))
    resp = make_response(xml_data, 200)
    resp.headers["Content-Type"] = "application/xml; charset=utf-8"
    resp.headers["Content-Disposition"] = "attachment; filename=dives.uddf"
    return resp
