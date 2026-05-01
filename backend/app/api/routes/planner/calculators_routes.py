# endpointy kalkulacek pro jednotlive vypocty (JWT otional)
from __future__ import annotations
from typing import List, Optional
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort
from marshmallow import Schema, fields
from app.utils.enums import DepthUnitEnum, PressureUnitEnum, VolumeUnitEnum
from app.utils.units import (
    UnitPrefs,
    convert_depth,
    convert_pressure,
    convert_volume,
)
from app.utils.jwt import get_identity
from app.services.unit_prefs_service import get_prefs_for_user
from app.planner.core.types import PlannerServiceError
from app.planner.calculators import (
    # SAC / RMV
    calc_rmv,
    calc_sac_bar_min,
    # Consumed / Required / DiveTime
    calc_consumed_gas,
    calc_required_gas_liters,
    calc_dive_time_from_tank,
    # NDL / Deco
    ndl_for_depth,
    ndl_table_for_depths,
    ndl_full_table,
    deco_stops_for_dive,
    resolve_mix_to_fo2,
    # Single-value calcs
    calc_ppo2,
    calc_mod,
    calc_best_mix,
    calc_ead,
    calc_end,
    calc_tank_gas_content_liters,
    calc_otu,
    calc_cns,
)

blp = Blueprint(
    "planner_calculators",
    __name__,
    url_prefix="/api/v1/planner/calculators",
    description="Kalkulačky pro plánování ponorů (RMV, SAC, NDL, deko, nitrox, ...)",
)

# UNIT PREFERENCES

def _get_user_prefs() -> UnitPrefs: # nacte jednotky prihlaseneho, jinak default [m]
    try:
        uid = get_identity()
        if uid and uid > 0:
            return get_prefs_for_user(uid)
    except Exception:
        pass
    return UnitPrefs()


def _depth_unit(payload_val: Optional[str], prefs: UnitPrefs) -> DepthUnitEnum: # vrati jednotku hloubky
    v = payload_val or prefs.depth.value
    try:
        return DepthUnitEnum(v)
    except ValueError:
        abort(400, message=f"Neplatná depth_unit: '{v}'. Použij 'm' nebo 'ft'.")


def _pressure_unit(payload_val: Optional[str], prefs: UnitPrefs) -> PressureUnitEnum:   # vrati jednotku tlaku
    v = payload_val or prefs.pressure.value
    try:
        return PressureUnitEnum(v)
    except ValueError:
        abort(400, message=f"Neplatná pressure_unit: '{v}'. Použij 'bar' nebo 'psi'.")


def _volume_unit(payload_val: Optional[str], prefs: UnitPrefs) -> VolumeUnitEnum:   # vrati jednotku objemu
    v = payload_val or prefs.volume.value
    try:
        return VolumeUnitEnum(v)
    except ValueError:
        abort(400, message=f"Neplatná volume_unit: '{v}'. Použij 'l' nebo 'cuft'.")


# SCHEMAS

# RMV / SAC 
class RMVRequestSchema(Schema):
    depth       = fields.Float(required=True)
    tank_size   = fields.Float(required=True, metadata={"description": "Objem lahve (l nebo cuft)"})
    dive_time   = fields.Float(required=True, metadata={"description": "Čas ponoru v minutách"})
    gas_consumed = fields.Float(required=True, metadata={"description": "Pokles tlaku v lahvi (bar nebo psi)"})
    depth_unit    = fields.String(load_default=None, allow_none=True)
    tank_unit     = fields.String(load_default=None, allow_none=True)
    pressure_unit = fields.String(load_default=None, allow_none=True)

class SACRequestSchema(Schema):
    depth        = fields.Float(required=True)
    dive_time    = fields.Float(required=True)
    gas_consumed = fields.Float(required=True, metadata={"description": "Pokles tlaku v lahvi (bar nebo psi)"})
    depth_unit    = fields.String(load_default=None, allow_none=True)
    pressure_unit = fields.String(load_default=None, allow_none=True)


# CONSUMED GAS 
class ConsumedGasRequestSchema(Schema):
    depth      = fields.Float(required=True)
    tank_size  = fields.Float(required=True, metadata={"description": "Objem lahve"})
    dive_time  = fields.Float(required=True)
    rmv        = fields.Float(required=True, metadata={"description": "RMV v l/min nebo cuft/min"})
    depth_unit    = fields.String(load_default=None, allow_none=True)
    tank_unit     = fields.String(load_default=None, allow_none=True)
    pressure_unit = fields.String(load_default=None, allow_none=True)
    volume_unit   = fields.String(load_default=None, allow_none=True, metadata={"description": "Jednotka pro RMV vstup"})


# REQUIRED GAS 
class RequiredGasRequestSchema(Schema):
    depth     = fields.Float(required=True)
    dive_time = fields.Float(required=True)
    rmv       = fields.Float(required=True, metadata={"description": "RMV v l/min nebo cuft/min"})
    depth_unit    = fields.String(load_default=None, allow_none=True)
    volume_unit   = fields.String(load_default=None, allow_none=True)


# DIVE TIME
class DiveTimeRequestSchema(Schema):
    depth        = fields.Float(required=True)
    tank_size    = fields.Float(required=True, metadata={"description": "Objem lahve"})
    gas_consumed = fields.Float(required=True, metadata={"description": "Dostupný tlak (bar nebo psi)"})
    rmv          = fields.Float(required=True, metadata={"description": "RMV v l/min nebo cuft/min"})
    depth_unit    = fields.String(load_default=None, allow_none=True)
    tank_unit     = fields.String(load_default=None, allow_none=True)
    pressure_unit = fields.String(load_default=None, allow_none=True)
    volume_unit   = fields.String(load_default=None, allow_none=True, metadata={"description": "Jednotka pro RMV vstup"})


# PPO2 / MOD / BEST MIX / EAD / END
class PPO2RequestSchema(Schema):
    f_o2       = fields.Float(required=True)
    depth      = fields.Float(required=True)
    depth_unit = fields.String(load_default=None, allow_none=True)

class MODRequestSchema(Schema):
    f_o2       = fields.Float(required=True)
    max_pp_o2  = fields.Float(load_default=1.4)
    depth_unit = fields.String(load_default=None, allow_none=True)

class BestMixRequestSchema(Schema):
    depth         = fields.Float(required=True)
    target_pp_o2  = fields.Float(load_default=1.4)
    depth_unit    = fields.String(load_default=None, allow_none=True)

class EADRequestSchema(Schema):
    depth      = fields.Float(required=True)
    f_o2       = fields.Float(required=True)
    depth_unit = fields.String(load_default=None, allow_none=True)

class ENDRequestSchema(Schema):
    depth      = fields.Float(required=True)
    f_o2       = fields.Float(required=True)
    f_he       = fields.Float(load_default=0.0)
    depth_unit = fields.String(load_default=None, allow_none=True)


# TANK GAS CONTENT
class TankGasContentRequestSchema(Schema):
    tank_size    = fields.Float(required=True)
    pressure     = fields.Float(required=True)
    tank_unit     = fields.String(load_default=None, allow_none=True)
    pressure_unit = fields.String(load_default=None, allow_none=True)


# OTU / CNS
class OTURequestSchema(Schema):
    pp_o2_ata = fields.Float(required=True)
    time_min  = fields.Float(required=True)


class CNSRequestSchema(Schema):
    f_o2       = fields.Float(required=True, metadata={"description": "FO2 frakce (0.21, 0.32...) nebo procenta (21, 32)"})
    depth      = fields.Float(required=True)
    time_min   = fields.Float(required=True, metadata={"description": "Čas na dně (BT) v minutách"})
    depth_unit = fields.String(load_default=None, allow_none=True)


# NDL / DECO STOPS
class NDLRequestSchema(Schema):
    depth      = fields.Float(required=True)
    mix        = fields.Raw(load_default=None, allow_none=True,metadata={"description": "'air', 'EAN32'...'EAN40', nebo FO2 číslo (0.32 nebo 32)"})
    f_o2       = fields.Float(load_default=None, allow_none=True,metadata={"description": "Alternativa k mix — frakce O2 (0.21..1.0)"})
    depth_unit = fields.String(load_default=None, allow_none=True)


class NDLTableRequestSchema(Schema):
    depths     = fields.List(fields.Float(), load_default=None, allow_none=True)
    mix        = fields.Raw(load_default=None, allow_none=True)
    f_o2       = fields.Float(load_default=None, allow_none=True)
    depth_unit = fields.String(load_default=None, allow_none=True)


class DecoStopsRequestSchema(Schema):
    depth          = fields.Float(required=True)
    bottom_time    = fields.Float(required=True, metadata={"description": "Čas na dně v minutách"})
    mix            = fields.Raw(load_default=None, allow_none=True,
                                 metadata={"description": "'air', 'EAN32'...'EAN40', nebo FO2 číslo"})
    f_o2           = fields.Float(load_default=None, allow_none=True)
    depth_unit     = fields.String(load_default=None, allow_none=True)


# ENDPOINTS

# RMV (Respiratory Minute Volume) l/m nebo cuft/min
@blp.route("/rmv", methods=["POST"])
@jwt_required(optional=True)
@blp.arguments(RMVRequestSchema)
@blp.response(200)
def calc_rmv_ep(payload):
    prefs = _get_user_prefs()
    du = _depth_unit(payload.get("depth_unit"), prefs)
    tu = _volume_unit(payload.get("tank_unit"), prefs)
    pu = _pressure_unit(payload.get("pressure_unit"), prefs)
    # Převod do metrické soustavy (m, l, bar)
    depth_m    = convert_depth(payload["depth"], du, DepthUnitEnum.METERS)
    tank_l     = convert_volume(payload["tank_size"], tu, VolumeUnitEnum.LITERS)
    pressure_b = convert_pressure(payload["gas_consumed"], pu, PressureUnitEnum.BAR)
    try:
        rmv_l_min = calc_rmv(
            depth=depth_m,
            tank_volume_l=tank_l,
            pressure_drop_bar=pressure_b,
            time_min=payload["dive_time"],
        )
    except (ValueError, PlannerServiceError) as e:
        abort(400, message=str(e))
    # Převod do preferované objemové jednotky
    rmv_out = convert_volume(rmv_l_min, VolumeUnitEnum.LITERS, prefs.volume)
    return {"result": round(rmv_out, 2), "unit": f"{prefs.volume.value}/min"}


# SAC (Surface Air Consumption) pokles tlaku za minut, bar/min nebo psi/min
@blp.route("/sac", methods=["POST"])
@jwt_required(optional=True)
@blp.arguments(SACRequestSchema)
@blp.response(200)
def calc_sac_ep(payload):

    prefs = _get_user_prefs()
    du = _depth_unit(payload.get("depth_unit"), prefs)
    pu = _pressure_unit(payload.get("pressure_unit"), prefs)
    depth_m    = convert_depth(payload["depth"], du, DepthUnitEnum.METERS)
    pressure_b = convert_pressure(payload["gas_consumed"], pu, PressureUnitEnum.BAR)

    try:
        sac = calc_sac_bar_min(
            depth=depth_m,
            pressure_drop_bar=pressure_b,
            time_min=payload["dive_time"],
        )
    except (ValueError, PlannerServiceError) as e:
        abort(400, message=str(e))

    # Výsledek v bar/min převod na psi/min pokud uživatel preferuje psi
    sac_out = convert_pressure(sac, PressureUnitEnum.BAR, prefs.pressure)
    return {"result": round(sac_out, 3), "unit": f"{prefs.pressure.value}/min"}


# Consumed Gas (spotreba plynu za ponor pro RMV)
@blp.route("/consumed-gas", methods=["POST"])
@jwt_required(optional=True)
@blp.arguments(ConsumedGasRequestSchema)
@blp.response(200)
def calc_consumed_gas_ep(payload):
    prefs = _get_user_prefs()
    du = _depth_unit(payload.get("depth_unit"), prefs)
    tu = _volume_unit(payload.get("tank_unit"), prefs)
    pu = _pressure_unit(payload.get("pressure_unit"), prefs)
    vu = _volume_unit(payload.get("volume_unit"), prefs)  # pro RMV vstup
    
    depth_m = convert_depth(payload["depth"], du, DepthUnitEnum.METERS)
    tank_l  = convert_volume(payload["tank_size"], tu, VolumeUnitEnum.LITERS)
    rmv_l   = convert_volume(payload["rmv"], vu, VolumeUnitEnum.LITERS)

    try:
        res = calc_consumed_gas(
            rmv_l_min=rmv_l,
            depth=depth_m,
            time_min=payload["dive_time"],
            tank_volume_l=tank_l,
        )
    except (ValueError, PlannerServiceError) as e:
        abort(400, message=str(e))

    consumed_vol  = convert_volume(res.consumed_l, VolumeUnitEnum.LITERS, prefs.volume)
    consumed_pres = convert_pressure(res.consumed_bar, PressureUnitEnum.BAR, prefs.pressure)
    return {
        "consumed_volume": round(consumed_vol, 1),
        "consumed_pressure": round(consumed_pres, 1),
        "unit_volume": prefs.volume.value,
        "unit_pressure": prefs.pressure.value,
    }


# Required Gas (potrebne mnozstvi pro ponor)
@blp.route("/required-gas", methods=["POST"])
@jwt_required(optional=True)
@blp.arguments(RequiredGasRequestSchema)
@blp.response(200)
def calc_required_gas_ep(payload):
    prefs = _get_user_prefs()
    du = _depth_unit(payload.get("depth_unit"), prefs)
    vu = _volume_unit(payload.get("volume_unit"), prefs)

    depth_m = convert_depth(payload["depth"], du, DepthUnitEnum.METERS)
    rmv_l   = convert_volume(payload["rmv"], vu, VolumeUnitEnum.LITERS)

    try:
        result_l = calc_required_gas_liters(
            rmv_l_min=rmv_l,
            depth=depth_m,
            time_min=payload["dive_time"],
        )
    except (ValueError, PlannerServiceError) as e:
        abort(400, message=str(e))

    result_out = convert_volume(result_l, VolumeUnitEnum.LITERS, prefs.volume)
    return {"result": round(result_out, 1), "unit": prefs.volume.value}


#  Dive Time (jak dlouho lze stravit v hloubce s danou zasobou )
@blp.route("/dive-time", methods=["POST"])
@jwt_required(optional=True)
@blp.arguments(DiveTimeRequestSchema)
@blp.response(200)
def calc_dive_time_ep(payload):
    prefs = _get_user_prefs()
    du = _depth_unit(payload.get("depth_unit"), prefs)
    tu = _volume_unit(payload.get("tank_unit"), prefs)
    pu = _pressure_unit(payload.get("pressure_unit"), prefs)
    vu = _volume_unit(payload.get("volume_unit"), prefs)

    depth_m    = convert_depth(payload["depth"], du, DepthUnitEnum.METERS)
    tank_l     = convert_volume(payload["tank_size"], tu, VolumeUnitEnum.LITERS)
    pressure_b = convert_pressure(payload["gas_consumed"], pu, PressureUnitEnum.BAR)
    rmv_l      = convert_volume(payload["rmv"], vu, VolumeUnitEnum.LITERS)

    try:
        time_min = calc_dive_time_from_tank(
            depth=depth_m,
            tank_volume_l=tank_l,
            pressure_available_bar=pressure_b,
            rmv_l_min=rmv_l,
        )
    except (ValueError, PlannerServiceError) as e:
        abort(400, message=str(e))

    return {"result": round(time_min, 1), "unit": "min"}


# ppO2 parcialni tlak kysliku [ATA/bar]
@blp.route("/ppo2", methods=["POST"])
@jwt_required(optional=True)
@blp.arguments(PPO2RequestSchema)
@blp.response(200)
def calc_ppo2_ep(payload):
    prefs = _get_user_prefs()
    du = _depth_unit(payload.get("depth_unit"), prefs)
    try:
        result = calc_ppo2(f_o2=payload["f_o2"], depth=payload["depth"], depth_unit=du)
    except Exception as e:
        abort(400, message=str(e))
    return {"result": result, "unit": "ATA"}


# MOD maximalni operacni hloubka pro dane FO2 a max ppO2
@blp.route("/mod", methods=["POST"])
@jwt_required(optional=True)
@blp.arguments(MODRequestSchema)
@blp.response(200)
def calc_mod_ep(payload):
    prefs = _get_user_prefs()
    du = _depth_unit(payload.get("depth_unit"), prefs)
    try:
        result = calc_mod(
            f_o2=payload["f_o2"],
            max_pp_o2=payload.get("max_pp_o2", 1.4),
            depth_unit=du,
        )
    except Exception as e:
        abort(400, message=str(e))
    return {"result": result, "unit": du.value}


# Best Mix doporucene FO2 pro danou hloubku a ppO2
@blp.route("/best-mix", methods=["POST"])
@jwt_required(optional=True)
@blp.arguments(BestMixRequestSchema)
@blp.response(200)
def calc_best_mix_ep(payload):
    prefs = _get_user_prefs()
    du = _depth_unit(payload.get("depth_unit"), prefs)
    try:
        result = calc_best_mix(
            depth=payload["depth"],
            target_pp_o2=payload.get("target_pp_o2", 1.4),
            depth_unit=du,
        )
    except Exception as e:
        abort(400, message=str(e))
    return {"result": result, "unit": "fraction (0..1)"}


# EAD (Equivalent Air Depth) ekvivalentni hloubka vzduchu pro nitrox
@blp.route("/ead", methods=["POST"])
@jwt_required(optional=True)
@blp.arguments(EADRequestSchema)
@blp.response(200)
def calc_ead_ep(payload):
    prefs = _get_user_prefs()
    du = _depth_unit(payload.get("depth_unit"), prefs)
    try:
        result = calc_ead(depth=payload["depth"], f_o2=payload["f_o2"], depth_unit=du)
    except Exception as e:
        abort(400, message=str(e))
    return {"result": result, "unit": du.value}


# END ekvivalentni narkoticka hloubka
@blp.route("/end", methods=["POST"])
@jwt_required(optional=True)
@blp.arguments(ENDRequestSchema)
@blp.response(200)
def calc_end_ep(payload):
    prefs = _get_user_prefs()
    du = _depth_unit(payload.get("depth_unit"), prefs)
    try:
        result = calc_end(
            depth=payload["depth"],
            f_o2=payload["f_o2"],
            f_he=payload.get("f_he", 0.0),
            depth_unit=du,
        )
    except Exception as e:
        abort(400, message=str(e))
    return {"result": result, "unit": du.value}


# Tank Gas Content, mnozstvi plynu v lahvi
@blp.route("/tank-gas-content", methods=["POST"])
@jwt_required(optional=True)
@blp.arguments(TankGasContentRequestSchema)
@blp.response(200)
def calc_tank_gas_content_ep(payload):
    prefs = _get_user_prefs()
    tu = _volume_unit(payload.get("tank_unit"), prefs)
    pu = _pressure_unit(payload.get("pressure_unit"), prefs)

    tank_l     = convert_volume(payload["tank_size"], tu, VolumeUnitEnum.LITERS)
    pressure_b = convert_pressure(payload["pressure"], pu, PressureUnitEnum.BAR)

    try:
        result_l = calc_tank_gas_content_liters(
            tank_volume_l=tank_l, pressure_bar=pressure_b
        )
    except Exception as e:
        abort(400, message=str(e))

    result_out = convert_volume(result_l, VolumeUnitEnum.LITERS, prefs.volume)
    return {"result": round(result_out, 1), "unit": prefs.volume.value}


# OTU kyslikova toxicita
@blp.route("/otu", methods=["POST"])
@jwt_required(optional=True)
@blp.arguments(OTURequestSchema)
@blp.response(200)
def calc_otu_ep(payload):
    try:
        result = calc_otu(pp_o2_ata=payload["pp_o2_ata"], time_min=payload["time_min"])
    except Exception as e:
        abort(400, message=str(e))
    return {"result": result, "unit": "OTU"}


# CNS zatez centralni nervove soustavy
@blp.route("/cns", methods=["POST"])
@jwt_required(optional=True)
@blp.arguments(CNSRequestSchema)
@blp.response(200)
def calc_cns_ep(payload):
    prefs = _get_user_prefs()
    du = _depth_unit(payload.get("depth_unit"), prefs)
    try:
        res = calc_cns(
            f_o2=payload["f_o2"],
            depth=payload["depth"],
            time_min=payload["time_min"],
            depth_unit=du,
        )
    except Exception as e:
        abort(400, message=str(e))
    return {
        "pp_o2_ata": res.pp_o2_ata,
        "mbt_min": res.mbt_min,
        "cns_percent": res.cns_percent,
        "warning": res.warning,
        "unit": "%",
    }


# NDL bez dekompresni limit (max cas v hloubce bez dekomprese)
@blp.route("/ndl", methods=["POST"])
@jwt_required(optional=True)
@blp.arguments(NDLRequestSchema)
@blp.response(200)
def calc_ndl_ep(payload):
    prefs = _get_user_prefs()
    du = _depth_unit(payload.get("depth_unit"), prefs)
    mix = payload.get("mix")
    f_o2 = payload.get("f_o2")
    try:
        result = ndl_for_depth(
            depth=payload["depth"],
            depth_unit=du,
            mix=mix,
            f_o2=f_o2,
        )
    except (ValueError, PlannerServiceError) as e:
        abort(400, message=str(e))
    return result


# NDL Table vraci celou tabulku pro danou smes
@blp.route("/ndl/table", methods=["POST"])
@jwt_required(optional=True)
@blp.arguments(NDLTableRequestSchema)
@blp.response(200)
def calc_ndl_table_ep(payload):
    prefs = _get_user_prefs()
    du = _depth_unit(payload.get("depth_unit"), prefs)
    depths = payload.get("depths")
    try:
        if depths:
            result = ndl_table_for_depths(
                depths=depths,
                depth_unit=du,
                mix=payload.get("mix"),
                f_o2=payload.get("f_o2"),
            )
        else:
            mix = payload.get("mix") or payload.get("f_o2")
            result = ndl_full_table(mix=mix, depth_unit=du)
    except (ValueError, PlannerServiceError) as e:
        abort(400, message=str(e))
    return result


# Deco Stops vraci deko zastavky pro danou (sems, hloubku a cas)
@blp.route("/deco-stops", methods=["POST"])
@jwt_required(optional=True)
@blp.arguments(DecoStopsRequestSchema)
@blp.response(200)
def calc_deco_stops_ep(payload):
    prefs = _get_user_prefs()
    du = _depth_unit(payload.get("depth_unit"), prefs)
    try:
        raw = deco_stops_for_dive(
            depth=payload["depth"],
            bottom_time_min=payload["bottom_time"],
            depth_unit=du,
            mix=payload.get("mix"),
            f_o2=payload.get("f_o2"),
        )
    except (ValueError, PlannerServiceError) as e:
        abort(400, message=str(e))

    stops_out = []
    for (stop_depth_m, stop_min) in raw.get("stops_m", []):
        stop_depth_out = convert_depth(float(stop_depth_m), DepthUnitEnum.METERS, prefs.depth)
        stops_out.append({
            "stop_depth": round(stop_depth_out, 1),
            "minutes": int(stop_min),
            "depth_unit": prefs.depth.value,
        })

    return {
        "depth": raw["depth"],
        "depth_unit": raw["depth_unit"],
        "bottom_time_min": raw["bottom_time_min"],
        "f_o2": raw["f_o2"],
        "is_deco": raw["is_deco"],
        "stops": stops_out,
        "source": raw["source"],
    }


