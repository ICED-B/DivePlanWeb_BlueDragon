"""
Endpoint pro komplexni planovac ponoru (multi-level, multi-gas, NDL/deko plan).
URL prefix: /api/v1/planner
Autentizace je volitelna (jwt_required optional=True) -- neprihlasen uzivatel
pouziva vychozi metricke jednotky.
"""
# Endpoint pro planovac ponoru (NDL/deko)
#(jwt_required optional=True) neprihlasen uzivatel
from __future__ import annotations
from typing import Optional
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort
from marshmallow import Schema, fields

from app.planner.planner_plan import (
    plan_dive_profile,
    TankInput,
    WaypointInput,
)
from app.planner.core.types import PlannerServiceError
from app.utils.enums import DepthUnitEnum
from app.utils.units import UnitPrefs, convert_depth
from app.utils.jwt import get_identity
from app.services.unit_prefs_service import get_prefs_for_user

blp = Blueprint("planner",__name__,
    url_prefix="/api/v1/planner",
    description="Plánovač ponorů (multi-level, multi-gas, NDL/deko plán)",
)

# UNIT PREFERENCES

def _get_user_prefs() -> UnitPrefs: # nacte jednotky prihlaseneho, jinak default
    try:
        uid = get_identity()
        if uid and uid > 0:
            return get_prefs_for_user(uid)
    except Exception:
        pass
    return UnitPrefs()


def _depth_unit_pref(payload_val: Optional[str], prefs: UnitPrefs) -> DepthUnitEnum:    # vrati jednotku hloubky
    v = payload_val or prefs.depth.value
    try:
        return DepthUnitEnum(v)
    except ValueError:
        abort(400, message=f"Neplatná depth_unit: '{v}'. Použij 'm' nebo 'ft'.")


# VSTUPNI SCHEMA

class TankInputSchema(Schema):  # chema pro lahev (tank_name, objem, tlak, FO2, FHe)."""
    tank_name            = fields.Raw(required=True, metadata={"description": "Jméno/label lahve — číslo (1) nebo text ('AIR_1', 'EAN32_deco'). Musí být unikátní."})
    size_l               = fields.Float(required=True, metadata={"description": "Objem lahve [l]"})
    pressure_bar         = fields.Float(required=True, metadata={"description": "Plnicí tlak [bar]"})
    backup_pressure_bar  = fields.Float(load_default=0.0, metadata={"description": "Záložní (bezpečnostní) tlak [bar] — tato část se nesmí spotřebovat. Výchozí 0."})
    f_o2                 = fields.Float(required=True, metadata={"description": "Podíl O₂: frakce (0.32) nebo % (32)"})
    f_he                 = fields.Float(load_default=0.0, metadata={"description": "Podíl He: frakce (0.0) nebo % (0)"})


class WaypointInputSchema(Schema):  # schema pro waypoint (bod v profilu)
    seq_num   = fields.Integer(required=True, metadata={"description": "Pořadové číslo waypontu (1, 2, 3…) — určuje pořadí zpracování"})
    depth     = fields.Float(required=True, metadata={"description": "Cílová hloubka (v jednotkách uživatele)"})
    time_min  = fields.Float(required=True, metadata={"description": "Čas v hloubce [min]"})
    tank_name = fields.Raw(required=True, metadata={"description": "Jméno lahve — musí odpovídat tank_name z tanks[]"})


class DivePlanRequestSchema(Schema):    # vstup planovce ponoru (sac, lahve, waypoints, volitelne)
    """Kompletni vstup pro planovac ponoru: SAC, lahve, waypoints a volitelna nastaveni."""
    sac_l_min          = fields.Float(required=True, metadata={"description": "SAC [l/min]"})
    allow_deco         = fields.Boolean(load_default=True, metadata={"description": "True = dekompresní ponor povolen. False = NDL režim (varování při překročení NDL)."})
    tanks              = fields.List(fields.Nested(TankInputSchema), required=True)
    waypoints          = fields.List(fields.Nested(WaypointInputSchema), required=True)
    ppo2_limit         = fields.Float(load_default=1.6, metadata={"description": "Max ppO₂ [ATA], výchozí 1.6"})
    descent_rate_m_min = fields.Float(load_default=10.0, metadata={"description": "Rychlost klesání [m/min]"})
    ascent_rate_m_min  = fields.Float(load_default=10.0, metadata={"description": "Rychlost stoupání [m/min]"})
    depth_unit         = fields.String(load_default=None, allow_none=True, metadata={"description": "'m' nebo 'ft' (výchozí: preference uživatele)"})


# VSTUPNI SCHEMA

class ProfileRowSchema(Schema): # vstupni schema segmentu
    segment_id   = fields.Integer()
    seg_type     = fields.String(metadata={"description": "'descent' | 'bottom' | 'ascent' | 'deco_stop'"})
    from_depth   = fields.Float()
    to_depth     = fields.Float()
    duration_min = fields.Float()
    tank_name    = fields.String()
    mix          = fields.String()


class DecoStopRowSchema(Schema):    # deko zastavky v hloubce
    stop_depth_m = fields.Float()
    duration_min = fields.Float()
    tank_name    = fields.String()
    mix          = fields.String()


class TankGasInfoSchema(Schema):    # prehled spotreby plynu pro lahev
    tank_name   = fields.String()
    mix         = fields.String()
    gas_sum_l   = fields.Float(metadata={"description": "Celkový plyn v lahvi [l]"})
    usable_l    = fields.Float(metadata={"description": "Použitelný plyn bez zálohy [l]"})
    backup_l    = fields.Float(metadata={"description": "Záložní rezerva [l]"})
    consumed_l  = fields.Float(metadata={"description": "Spotřeba během ponoru [l]"})
    remaining_l = fields.Float(metadata={"description": "Zbývající plyn [l]"})


class PlanSummarySchema(Schema):    # souhrn celeho planu ponoru    (cas, hloubky, plyn, CNS, OTU, varováni)
    total_time_min  = fields.Float()
    avg_depth_m     = fields.Float()
    max_depth_m     = fields.Float()
    ndl_min         = fields.Integer(allow_none=True)
    is_deco         = fields.Boolean()
    gas_sum_l       = fields.Float(metadata={"description": "Celkový plyn všech lahví [l]"})
    consumed_gas_l  = fields.Float(metadata={"description": "Celková spotřeba [l]"})
    remaining_gas_l = fields.Float(metadata={"description": "Celkový zůstatek [l]"})
    tanks_gas       = fields.List(
        fields.Nested(TankGasInfoSchema),
        metadata={"description": "Přehled spotřeby na každou lahev"},
    )
    cns_total_pct   = fields.Float()
    otu_total       = fields.Float()
    mods            = fields.Dict(
        keys=fields.String(),
        values=fields.Float(),
        metadata={"description": "MOD pro každou lahev v preferované hloubkové jednotce — {tank_name: mod_value}"},
    )
    deco_source     = fields.String()
    warnings        = fields.List(fields.String())


class DivePlanResponseSchema(Schema):   # output planovace (profil segmentu, deko stops, souhrn a jednotka hloubky)
    profile    = fields.List(fields.Nested(ProfileRowSchema))
    deco_stops = fields.List(fields.Nested(DecoStopRowSchema))
    summary    = fields.Nested(PlanSummarySchema)
    depth_unit = fields.String()


# ENDPOINT

@blp.route("/plan", methods=["POST"])
@jwt_required(optional=True)
@blp.arguments(DivePlanRequestSchema)
@blp.response(200, DivePlanResponseSchema)
def plan_dive_ep(payload):
    # planovac ponoru
    # intput [SAC, lahve, waypointy a volitelne]
    # output [profil, deko stops, souhrn, spotreby, varovani]

    prefs = _get_user_prefs()
    du = _depth_unit_pref(payload.get("depth_unit"), prefs)

    # LAHVE
    tanks: list[TankInput] = []
    for t in payload["tanks"]:
        f_o2 = float(t["f_o2"])
        f_he = float(t.get("f_he", 0.0))
        if f_o2 > 1.0:
            f_o2 /= 100.0
        if f_he > 1.0:
            f_he /= 100.0
        tanks.append(TankInput(
            tank_name=str(t["tank_name"]),
            size_l=float(t["size_l"]),
            pressure_bar=float(t["pressure_bar"]),
            backup_pressure_bar=float(t.get("backup_pressure_bar", 0.0)),
            f_o2=round(f_o2, 4),
            f_he=round(f_he, 4),
        ))

    # WAYPOINTS
    waypoints: list[WaypointInput] = []
    for wp in payload["waypoints"]:
        depth_m = float(convert_depth(wp["depth"], du, DepthUnitEnum.METERS))
        waypoints.append(WaypointInput(
            seq_num=int(wp["seq_num"]),
            depth_m=depth_m,
            time_min=float(wp["time_min"]),
            tank_name=str(wp["tank_name"]),
        ))

    try:
        result = plan_dive_profile(
            sac_l_min=float(payload["sac_l_min"]),
            tanks=tanks,
            waypoints=waypoints,
            allow_deco=bool(payload.get("allow_deco", True)),
            ppo2_limit=float(payload.get("ppo2_limit", 1.6)),
            descent_rate_m_min=float(payload.get("descent_rate_m_min", 10.0)),
            ascent_rate_m_min=float(payload.get("ascent_rate_m_min", 10.0)),
        )
    except (ValueError, PlannerServiceError) as e:
        abort(400, message=str(e))

    # PREVOD HLOUBEK
    def _cd(d_m: float) -> float:
        return round(float(convert_depth(d_m, DepthUnitEnum.METERS, prefs.depth)), 1)

    profile_out = [
        {
            "segment_id":  row.segment_id,
            "seg_type":    row.seg_type,
            "from_depth":  _cd(row.from_depth),
            "to_depth":    _cd(row.to_depth),
            "duration_min": row.duration_min,
            "tank_name":   row.tank_name,
            "mix":         row.mix,
        }
        for row in result.profile
    ]

    deco_stops_out = [
        {
            "stop_depth_m": _cd(stop["stop_depth_m"]),
            "duration_min": stop["duration_min"],
            "tank_name":    stop["tank_name"],
            "mix":          stop["mix"],
        }
        for stop in result.deco_stops
    ]

    s = result.summary

    mods_out = {
        name: round(float(convert_depth(mod_m, DepthUnitEnum.METERS, prefs.depth)), 1)
        for name, mod_m in s.mods.items()
    }

    tanks_gas_out = [
        {
            "tank_name":   tg.tank_name,
            "mix":         tg.mix,
            "gas_sum_l":   tg.gas_sum_l,
            "usable_l":    tg.usable_l,
            "backup_l":    tg.backup_l,
            "consumed_l":  tg.consumed_l,
            "remaining_l": tg.remaining_l,
        }
        for tg in s.tanks_gas
    ]

    return {
        "profile":    profile_out,
        "deco_stops": deco_stops_out,
        "summary": {
            "total_time_min":  s.total_time_min,
            "avg_depth_m":     _cd(s.avg_depth_m),
            "max_depth_m":     _cd(s.max_depth_m),
            "ndl_min":         s.ndl_min,
            "is_deco":         s.is_deco,
            "gas_sum_l":       s.gas_sum_l,
            "consumed_gas_l":  s.consumed_gas_l,
            "remaining_gas_l": s.remaining_gas_l,
            "tanks_gas":       tanks_gas_out,
            "cns_total_pct":   s.cns_total_pct,
            "otu_total":       s.otu_total,
            "mods":            mods_out,
            "deco_source":     s.deco_source,
            "warnings":        s.warnings,
        },
        "depth_unit": prefs.depth.value,
    }
