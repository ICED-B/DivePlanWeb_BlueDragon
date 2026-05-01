# globalni statistiky pro vsechny
from __future__ import annotations
from app.services.extended_stats_service import (
    get_global_gas_mix_stats,
    get_global_tank_stats,
    get_global_tag_stats,
    get_global_dive_event_stats,
    get_global_circuit_stats,
    get_global_license_stats,
    get_global_site_country_stats,
    get_global_site_region_stats,
)

from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from marshmallow import Schema, fields

from app.services.stats_service import (
    get_global_stats,
    StatsServiceError,
)

blp = Blueprint(
    "stats",
    __name__,
    url_prefix="/api/v1/stats",
    description="Globální statistiky ponorů (veřejné, bez přihlášení)",
)

class StatsBasicStatsSchema(Schema):
    dives_count = fields.Int()
    total_duration_min = fields.Float()
    avg_duration_min = fields.Float()
    max_depth_m = fields.Float()
    avg_depth_m = fields.Float()
    avg_temp_c = fields.Float(allow_none=True)

class StatsTopSiteSchema(Schema):
    site_name = fields.String()
    dives = fields.Int()

class StatsDeepDiveSchema(Schema):
    id = fields.Int()
    start_time = fields.String(allow_none=True)
    max_depth_m = fields.Float(allow_none=True)
    duration_min = fields.Float(allow_none=True)
    site = fields.String(allow_none=True)
    diver_name = fields.String(allow_none=True)

class GlobalStatsResponseSchema(Schema):
    basic = fields.Nested(StatsBasicStatsSchema)
    top_sites = fields.List(fields.Nested(StatsTopSiteSchema))
    top_deep_dives = fields.List(fields.Nested(StatsDeepDiveSchema))


@blp.route("/global")
@jwt_required(optional=True)
@blp.response(200, GlobalStatsResponseSchema)
def global_stats():
    try:
        return get_global_stats(limit_top_sites=5, top_deep_limit=10)
    except StatsServiceError as e:
        abort(400, message=str(e))

class GlobalGasMixStatSchema(Schema):
    gas_mix_id = fields.Int()
    name = fields.String(allow_none=True)
    gas_type = fields.String()
    o2_percent = fields.Float(allow_none=True)
    he_percent = fields.Float(allow_none=True)
    uses = fields.Int()

class GlobalTankStatSchema(Schema):
    tank_id = fields.Int()
    volume_l = fields.Float(allow_none=True)
    work_pressure_bar = fields.Float(allow_none=True)
    material = fields.String(allow_none=True)
    uses = fields.Int()

class GlobalTagStatSchema(Schema):
    name = fields.String()
    uses = fields.Int()

class GlobalEventStatSchema(Schema):
    type = fields.String()
    uses = fields.Int()

class GlobalCircuitStatSchema(Schema):
    breathing_system = fields.String()
    dives = fields.Int()

class GlobalLicenseStatSchema(Schema):
    agency = fields.String(allow_none=True)
    certification = fields.String(allow_none=True)
    dives = fields.Int()

class GlobalCountryStatSchema(Schema):
    country = fields.String()
    dives = fields.Int()

class GlobalRegionStatSchema(Schema):
    region = fields.String()
    dives = fields.Int()


class GlobalGasMixStatListSchema(Schema):
    items = fields.List(fields.Nested(GlobalGasMixStatSchema), required=True)

class GlobalTankStatListSchema(Schema):
    items = fields.List(fields.Nested(GlobalTankStatSchema), required=True)

class GlobalTagStatListSchema(Schema):
    items = fields.List(fields.Nested(GlobalTagStatSchema), required=True)

class GlobalEventStatListSchema(Schema):
    items = fields.List(fields.Nested(GlobalEventStatSchema), required=True)

class GlobalCircuitStatListSchema(Schema):
    items = fields.List(fields.Nested(GlobalCircuitStatSchema), required=True)

class GlobalLicenseStatListSchema(Schema):
    items = fields.List(fields.Nested(GlobalLicenseStatSchema), required=True)

class GlobalCountryStatListSchema(Schema):
    items = fields.List(fields.Nested(GlobalCountryStatSchema), required=True)

class GlobalRegionStatListSchema(Schema):
    items = fields.List(fields.Nested(GlobalRegionStatSchema), required=True)


@blp.route("/global/gas-mix")
@jwt_required(optional=True)
@blp.response(200, GlobalGasMixStatListSchema)
def global_gas_mix_stats():
    return {"items": get_global_gas_mix_stats(limit=10)}


@blp.route("/global/tanks")
@jwt_required(optional=True)
@blp.response(200, GlobalTankStatListSchema)
def global_tank_stats():
    return {"items": get_global_tank_stats(limit=10)}


@blp.route("/global/tags")
@jwt_required(optional=True)
@blp.response(200, GlobalTagStatListSchema)
def global_tag_stats():
    return {"items": get_global_tag_stats(limit=10)}


@blp.route("/global/events")
@jwt_required(optional=True)
@blp.response(200, GlobalEventStatListSchema)
def global_event_stats():
    return {"items": get_global_dive_event_stats(limit=10)}


@blp.route("/global/circuits")
@jwt_required(optional=True)
@blp.response(200, GlobalCircuitStatListSchema)
def global_circuit_stats():
    return {"items": get_global_circuit_stats(limit=10)}


@blp.route("/global/licenses")
@jwt_required(optional=True)
@blp.response(200, GlobalLicenseStatListSchema)
def global_license_stats():
    return {"items": get_global_license_stats(limit=10)}


@blp.route("/global/countries")
@jwt_required(optional=True)
@blp.response(200, GlobalCountryStatListSchema)
def global_country_stats():
    return {"items": get_global_site_country_stats(limit=10)}


@blp.route("/global/regions")
@jwt_required(optional=True)
@blp.response(200, GlobalRegionStatListSchema)
def global_region_stats():
    return {"items": get_global_site_region_stats(limit=10)}
