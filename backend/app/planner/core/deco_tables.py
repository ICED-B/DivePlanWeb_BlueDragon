# backend/app/planner/core/deco_tables.py
from __future__ import annotations

# Lookup NDL a deko planu z tabulek
# tabulky jsou lazy-load z deco_tables/ (pokud neni k dispozici pouzije se fallback NDL z vzduchu)
from typing import Dict, Any, Optional

# Globalni cache tabulek naplni se pri prvnim volani _load_deco_tables()
_DECO_TABLES: Dict[str, Dict[int, Dict[int, list[tuple[int, int]]]]] = {}


def _load_deco_tables() -> None:    # lazy-load vsech dostupnych deko tabulek z deco_tables/
    global _DECO_TABLES
    if _DECO_TABLES:    # Tabulky uz jsou nacteny znovu nezatezujeme import
        return

    candidates = {
        "air": "app.planner.deco_tables.air",
        "ean32": "app.planner.deco_tables.ean32",
        "ean34": "app.planner.deco_tables.ean34",
        "ean36": "app.planner.deco_tables.ean36",
        "ean38": "app.planner.deco_tables.ean38",
        "ean40": "app.planner.deco_tables.ean40",
    }

    for key, module_name in candidates.items():
        try:
            mod = __import__(module_name, fromlist=["TABLE"])
            table = getattr(mod, "TABLE", None)
            if isinstance(table, dict):
                _DECO_TABLES[key] = table
        except Exception:
            # Modul neni dostupny nebo je prazdny -- preskocime bez chyby
            continue


def _pick_table_for_f_o2(f_o2: Optional[float]) -> str:     # vybere klic tabulky podle frakce O2 (vzduch FO2=0.21, neznamy plyn je air)
    if f_o2 is None:
        return "air"
    f = round(float(f_o2), 2)
    if 0.31 <= f <= 0.33:
        return "ean32"
    if 0.33 < f <= 0.35:
        return "ean34"
    if 0.35 < f <= 0.37:
        return "ean36"
    if 0.37 < f <= 0.39:
        return "ean38"
    if 0.39 < f <= 0.41:
        return "ean40"
    return "air"            # Vzduch nebo smes mimo definovane intervaly


def _select_depth_table(
    table: Dict[int, Dict[int, list[tuple[int, int]]]], depth_m: float
) -> Optional[Dict[int, list[tuple[int, int]]]]:    # vybere pro nejblizsi def hloubku <= zadana hloubka
    if not table:
        return None
    keys = sorted(table.keys())
    depth_int = int(round(depth_m))
    candidate = None
    for k in keys:
        if k <= depth_int:
            candidate = k           # Posledni klic, ktery je <= hloubce, bude pouzit
    if candidate is not None:
        return table[candidate] 
    return table[keys[0]]       # Hloubka je mensi nez nejmensi definovana


def _select_stops_for_time(
    depth_table: Dict[int, list[tuple[int, int]]], bottom_time_min: float
) -> list[tuple[int, int]]:         # vraci deko zastavky pro zadane casy na dne, vybira nejmensi def cas ktery je >= bottom_time_min
    times = sorted(depth_table.keys())
    bt = int(round(bottom_time_min))
    for t in times:
        if bt <= t:
            return depth_table[t]       # Cas je delsi nez nejdelsi definovany
    return depth_table[times[-1]]


# Jednoduchy fallback NDL pro vzduch [hloubka_m -> NDL_min] (kdyz nejsou tabulky dostupne)
_FALLBACK_AIR_NDL_M = {
    12: 140,
    15: 80,
    18: 55,
    21: 45,
    25: 30,
    30: 20,
    35: 15,
}


def _fallback_ndl(depth_m: float) -> int:   # kdyz nelze najit vhodnout tabulku (NDL v min)
    keys = sorted(_FALLBACK_AIR_NDL_M.keys())
    d = float(depth_m)
    if d <= keys[0]:
        return _FALLBACK_AIR_NDL_M[keys[0]]
    if d >= keys[-1]:
        return _FALLBACK_AIR_NDL_M[keys[-1]]
    for i in range(len(keys) - 1):
        d0, d1 = keys[i], keys[i + 1]
        if d0 <= d <= d1:
            ndl0, ndl1 = _FALLBACK_AIR_NDL_M[d0], _FALLBACK_AIR_NDL_M[d1]
            t = (d - d0) / (d1 - d0)            # Linearni interpolace mezi dvema sousednimi body
            return int(round(ndl0 + t * (ndl1 - ndl0)))
    return _FALLBACK_AIR_NDL_M[keys[-1]]


def get_deco_plan_from_tables(
    depth_m: float,
    bottom_time_min: float,
    f_o2: Optional[float] = None,
) -> Optional[Dict[str, Any]]:      # vrati NDL a deko stops z tabulek pro hloubku cas a smes
    _load_deco_tables()
    table_key = _pick_table_for_f_o2(f_o2)
    table = _DECO_TABLES.get(table_key)
    if not table:
        return None

    depth_table = _select_depth_table(table, depth_m)
    if not depth_table:
        return None

    stops = _select_stops_for_time(depth_table, bottom_time_min)
    # NDL = nejmensi cas v subtabulce pro tuto hloubku (prvni zaznam)
    ndl = sorted(depth_table.keys())[0]
    is_deco = bottom_time_min > ndl

    return {
        "ndl": ndl,
        "is_deco": is_deco,
        "stops": stops,
        "source": table_key,
    }


def plan_dive(
    depth_m: float,
    bottom_time_min: float,
    f_o2: Optional[float] = None,
) -> Dict[str, Any]:        # NDL/deko plan z tabulek, kdyz je table k dispozici pouzije se, jinak vraci fallback z vzduchovych NDL
    plan = get_deco_plan_from_tables(depth_m, bottom_time_min, f_o2=f_o2)
    if plan is not None:
        return plan

    ndl = _fallback_ndl(depth_m)    # Tabulka neni k dispozici, pouzijeme fallback NDL pro vzduch
    return {
        "ndl": ndl,
        "is_deco": bottom_time_min > ndl,
        "stops": [(3, 1)] if bottom_time_min <= ndl else [],        # Minimalni bezpecnostni zastavka i v NDL rezim
        "source": "fallback",
    }
