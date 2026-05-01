# statistiky pro prihlaseneho uzivatele (pouze jeho data)
from __future__ import annotations
from app.services.extended_stats_service import (
    get_user_gas_mix_stats,
    get_user_tank_stats,
    get_user_tag_stats,
    get_user_dive_event_stats,
    get_user_circuit_stats,
    get_user_license_stats,
    get_user_site_country_stats,
    get_user_site_region_stats,
)

from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from marshmallow import Schema, fields

from app.services.stats_service import (
    get_user_stats,
    StatsServiceError,
)
from app.utils.jwt import get_identity

blp = Blueprint(
    "user_stats",
    __name__,
    url_prefix="/api/v1/user-stats",
    description="User-only aggregated stats (my dives only)",
)

class UserBasicStatsSchema(Schema):
    dives_count = fields.Int()
    total_duration_min = fields.Float()
    avg_duration_min = fields.Float()
    max_depth_m = fields.Float()
    avg_depth_m = fields.Float()
    avg_temp_c = fields.Float(allow_none=True)


class UserTopSiteSchema(Schema):
    site_name = fields.String()
    dives = fields.Int()


class UserRecentDiveSchema(Schema):
    id = fields.Int()
    start_time = fields.String(allow_none=True)
    duration_min = fields.Float(allow_none=True)
    max_depth_m = fields.Float(allow_none=True)
    site = fields.String(allow_none=True)


class UserDeepDiveSchema(Schema):
    id = fields.Int()
    start_time = fields.String(allow_none=True)
    max_depth_m = fields.Float(allow_none=True)
    duration_min = fields.Float(allow_none=True)
    site = fields.String(allow_none=True)
    # u user_stats bude typicky None, necháváme pro kompatibilitu
    diver_name = fields.String(allow_none=True)


class UserUserStatsResponseSchema(Schema):
    basic = fields.Nested(UserBasicStatsSchema)
    top_sites = fields.List(fields.Nested(UserTopSiteSchema))
    recent_dives = fields.List(fields.Nested(UserRecentDiveSchema))
    top_deep_dives = fields.List(fields.Nested(UserDeepDiveSchema))



class UserGasMixStatSchema(Schema):
    gas_mix_id = fields.Int()
    name = fields.String(allow_none=True)
    gas_type = fields.String()
    o2_percent = fields.Float(allow_none=True)
    he_percent = fields.Float(allow_none=True)
    uses = fields.Int()


class UserTankStatSchema(Schema):
    tank_id = fields.Int()
    volume_l = fields.Float(allow_none=True)
    work_pressure_bar = fields.Float(allow_none=True)
    material = fields.String(allow_none=True)
    uses = fields.Int()


class UserTagStatSchema(Schema):
    tag_id = fields.Int()
    name = fields.String()
    uses = fields.Int()


class UserEventStatSchema(Schema):
    type = fields.String()
    uses = fields.Int()


class UserCircuitStatSchema(Schema):
    breathing_system = fields.String()
    dives = fields.Int()


class UserLicenseStatSchema(Schema):
    license_id = fields.Int()
    agency = fields.String(allow_none=True)
    certification = fields.String(allow_none=True)
    dives = fields.Int()


class UserCountryStatSchema(Schema):
    country = fields.String()
    dives = fields.Int()


class UserRegionStatSchema(Schema):
    region = fields.String()
    dives = fields.Int()


# Obalove schemata s klicem "items" pro seznam vysledku
class UserGasMixStatListSchema(Schema):
    items = fields.List(fields.Nested(UserGasMixStatSchema), required=True)

class UserTankStatListSchema(Schema):
    items = fields.List(fields.Nested(UserTankStatSchema), required=True)

class UserTagStatListSchema(Schema):
    items = fields.List(fields.Nested(UserTagStatSchema), required=True)

class UserEventStatListSchema(Schema):
    items = fields.List(fields.Nested(UserEventStatSchema), required=True)

class UserCircuitStatListSchema(Schema):
    items = fields.List(fields.Nested(UserCircuitStatSchema), required=True)

class UserLicenseStatListSchema(Schema):
    items = fields.List(fields.Nested(UserLicenseStatSchema), required=True)

class UserCountryStatListSchema(Schema):
    items = fields.List(fields.Nested(UserCountryStatSchema), required=True)

class UserRegionStatListSchema(Schema):
    items = fields.List(fields.Nested(UserRegionStatSchema), required=True)



# Endpointy

@blp.route("/", methods=["GET"])
@jwt_required()
@blp.response(200, UserUserStatsResponseSchema)
def user_stats():
    current_user_id = get_identity()
    try:
        data = get_user_stats(user_id=current_user_id,
                              limit_recent=5, top_deep_limit=5)
    except StatsServiceError as e:
        abort(400, message=str(e))
    return data


@blp.route("/gas-mix")
@jwt_required()
@blp.response(200, UserGasMixStatListSchema)
def user_gas_mix_stats():
    return {"items": get_user_gas_mix_stats(get_identity(), limit=5)}


@blp.route("/tanks")
@jwt_required()
@blp.response(200, UserTankStatListSchema)
def user_tank_stats():
    return {"items": get_user_tank_stats(get_identity(), limit=5)}


@blp.route("/tags")
@jwt_required()
@blp.response(200, UserTagStatListSchema)
def user_tag_stats():
    return {"items": get_user_tag_stats(get_identity(), limit=5)}


@blp.route("/events")
@jwt_required()
@blp.response(200, UserEventStatListSchema)
def user_event_stats():
    return {"items": get_user_dive_event_stats(get_identity(), limit=5)}


@blp.route("/circuits")
@jwt_required()
@blp.response(200, UserCircuitStatListSchema)
def user_circuit_stats():
    return {"items": get_user_circuit_stats(get_identity(), limit=5)}


@blp.route("/licenses")
@jwt_required()
@blp.response(200, UserLicenseStatListSchema)
def user_license_stats():
    return {"items": get_user_license_stats(get_identity(), limit=5)}


@blp.route("/countries")
@jwt_required()
@blp.response(200, UserCountryStatListSchema)
def user_country_stats():
    return {"items": get_user_site_country_stats(get_identity(), limit=5)}


@blp.route("/regions")
@jwt_required()
@blp.response(200, UserRegionStatListSchema)
def user_region_stats():
    return {"items": get_user_site_region_stats(get_identity(), limit=5)}
