from __future__ import annotations
# NDL a tabulkove dekompresni vypocty
# zjistuje NDL pro danou hloubku, cela tabulka NDL, deko zastavky pro danou hloubku a cas

from typing import Dict, Any, Iterable, List, Optional, Union

from app.utils.enums import DepthUnitEnum
from app.utils.units import convert_depth
from app.planner.core.types import Number
from app.planner.core.deco_tables import plan_dive as _plan_dive, get_deco_plan_from_tables

# Nazvy smesi na hodnotu FO2 (frakce)
_MIX_TO_FO2: Dict[str, float] = {
    "air": 0.21,
    "ean32": 0.32,
    "ean34": 0.34,
    "ean36": 0.36,
    "ean38": 0.38,
    "ean40": 0.40,
}


def resolve_mix_to_fo2(mix: Union[str, float, None]) -> Optional[float]:
    # prevod nazvu smesi na cislo FO2
    if mix is None:
        return None
    if isinstance(mix, (int, float)):
        v = float(mix)
        return round(v / 100.0, 4) if v > 1.0 else round(v, 4)        # Hodnoty > 1.0 jsou procenta (napr. 32 = 32 % = 0.32)
    mix_str = str(mix).strip().lower()
    if mix_str in _MIX_TO_FO2:
        return _MIX_TO_FO2[mix_str]
    try:
        v = float(mix_str)
        return round(v / 100.0, 4) if v > 1.0 else round(v, 4)
    except ValueError:
        raise ValueError(
            f"Neznama smes: '{mix}'. "
            "Pouzij 'air', 'EAN32', 'EAN34', 'EAN36', 'EAN38', 'EAN40' nebo FO2 cislo (0.32 nebo 32)."
        )


def ndl_for_depth(
    depth: Number,
    depth_unit: DepthUnitEnum = DepthUnitEnum.METERS,
    f_o2: Optional[float] = None,
    mix: Union[str, float, None] = None,
) -> Dict[str, Any]:
    # NDL pro danou hloubku a smes
    if mix is not None:
        f_o2 = resolve_mix_to_fo2(mix)
    depth_m = float(convert_depth(depth, depth_unit, DepthUnitEnum.METERS))
    base = _plan_dive(depth_m=depth_m, bottom_time_min=0.0, f_o2=f_o2)     # Cas 0 -> tabulka vrati jen NDL (bez deko zastavek)
    return {
        "depth": float(depth),
        "depth_unit": depth_unit.value,
        "f_o2": round(float(f_o2), 4) if f_o2 is not None else None,
        "ndl_min": int(base.get("ndl")),
        "source": base.get("source"),
    }


def ndl_full_table(
    mix: Union[str, float, None] = None,
    depth_unit: DepthUnitEnum = DepthUnitEnum.METERS,
) -> List[Dict[str, Any]]:
    # vraci kompletni NDL tabulku z internich hodnot pro smes
    from app.planner.core.deco_tables import _load_deco_tables, _DECO_TABLES, _pick_table_for_f_o2

    f_o2 = resolve_mix_to_fo2(mix) if mix is not None else 0.21
    _load_deco_tables()
    table_key = _pick_table_for_f_o2(f_o2)    # Vyber tabulky podle FO2 smesi
    table = _DECO_TABLES.get(table_key)
    if not table:
        return []

    result = []
    for depth_m_int in sorted(table.keys()):
        depth_table = table[depth_m_int]
        ndl = sorted(depth_table.keys())[0]         # Nejmensi casovy klic = NDL pro tuto hloubku
        depth_out = float(convert_depth(depth_m_int, DepthUnitEnum.METERS, depth_unit))
        result.append({
            "depth": depth_out,
            "depth_unit": depth_unit.value,
            "ndl_min": ndl,
            "source": table_key,
        })
    return result


def deco_stops_for_dive(
    depth: Number,
    bottom_time_min: float,
    depth_unit: DepthUnitEnum = DepthUnitEnum.METERS,
    f_o2: Optional[float] = None,
    mix: Union[str, float, None] = None,
) -> Dict[str, Any]:
    # deko zastavky pro input (hloubka + cas + smes) kdyz is_deco=Fasle seznam je prazdny
    if mix is not None:
        f_o2 = resolve_mix_to_fo2(mix)
    depth_m = float(convert_depth(depth, depth_unit, DepthUnitEnum.METERS))
    plan = _plan_dive(depth_m=depth_m, bottom_time_min=float(bottom_time_min), f_o2=f_o2)
    return {
        "depth": float(depth),
        "depth_unit": depth_unit.value,
        "bottom_time_min": float(bottom_time_min),
        "f_o2": round(float(f_o2), 4) if f_o2 is not None else None,
        "is_deco": bool(plan.get("is_deco")),
        "stops_m": list(plan.get("stops", [])),   # [(depth_m, minutes)]
        "source": plan.get("source"),
    }


def ndl_table_for_depths(
    depths: Iterable[Number],
    depth_unit: DepthUnitEnum = DepthUnitEnum.METERS,
    f_o2: Optional[float] = None,
    mix: Union[str, float, None] = None,
) -> List[Dict[str, Any]]:
    # NDL tabulka pro sadu hloubek
    if mix is not None:
        f_o2 = resolve_mix_to_fo2(mix)
    return [ndl_for_depth(d, depth_unit=depth_unit, f_o2=f_o2) for d in depths]
