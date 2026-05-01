from __future__ import annotations
# Planner   vychazi ze zadani SAC, allow_deko, lahve waypoints a volitelne data
# vraco profil v bodech jako tabulka, deko zastavky nebo jen pauza a souhrn (avg, gas, CNS, OTU, MOD, NDL/DL)
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple

from app.planner.core.deco_tables import plan_dive
from app.planner.calculators.otu import calc_otu


# NOAA CNS tabulka, ceiling metoda
# klic = ppO2 [ATA], hodnota = MBT (Maximum Bottom Time) [min]
_NOAA_MBT: Dict[float, float] = {
    0.6: 720.0,
    0.7: 570.0,
    0.8: 450.0,
    0.9: 360.0,
    1.0: 300.0,
    1.1: 240.0,
    1.2: 210.0,
    1.3: 180.0,
    1.4: 150.0,
    1.5: 120.0,
    1.6:  45.0,
}
# Serazene klice pro bisekci/ceiling lookup
_NOAA_KEYS = sorted(_NOAA_MBT.keys())


def _ceiling_mbt(pp: float) -> float:
    # vraci MBT pro dano ppO2 metodou CEILING (nejblizsi vyssi hodnota z tabulky)
    # [Pokud ppO2 < 0.6 ATA, vraci 0.0 (CNS toxicita neni relevantni)], [Pokud ppO2 > 1.6 ATA, vraci MBT pro 1.6 (nejprisnejsi limit)]
    if pp < _NOAA_KEYS[0]:
        # pod prahem, zadna CNS toxicita
        return 0.0
    for k in _NOAA_KEYS:
        if pp <= k:
            # ceiling: prvni klic >= pp
            return _NOAA_MBT[k]
    # nad maximem tabulky pouzijeme nejprisnejsi limit
    return _NOAA_MBT[_NOAA_KEYS[-1]]


# TRIDY INPUT DAT

@dataclass
class TankInput:
    tank_name: str              # name lahve
    size_l: float               # objem lahve [l]
    pressure_bar: float         # plnici tlak [bar]
    backup_pressure_bar: float  # zalozni tlak, (tato cast se nesmi spotrebovat) [bar]
    f_o2: float                 # frakce O2 (0.0-1.0)
    f_he: float = 0.0           # frakce He (0.0-1.0)

    @property
    def gas_sum_l(self) -> float:   # celkovy plyn v lahvi [l] = objem * tlak
        return self.size_l * self.pressure_bar

    @property
    def usable_gas_l(self) -> float:    # pouzitelny plyn bez zalohy (castka nad backup_pressure_bar)
        return self.size_l * max(0.0, self.pressure_bar - self.backup_pressure_bar)

    @property
    def backup_gas_l(self) -> float:    # zalozni rezerva plynu [l] = objem * backup_pressure
        return self.size_l * self.backup_pressure_bar

    @property
    def mix_label(self) -> str:     # nazev smesi (Air / EAN32 / Trimix xx/yy)
        if self.f_he > 0.005:
            return f"Trimix {round(self.f_o2 * 100)}/{round(self.f_he * 100)}"
        pct = round(self.f_o2 * 100)
        if pct == 21:
            return "Air"
        return f"EAN{pct}"

    def mod_m(self, ppo2_limit: float) -> float:
        # MOD (maximum Operating Depth) v metrech pro ppO2 limit [MOD = (ppO2_limit / FO2 -1) * 10]
        if self.f_o2 <= 0:
            return 0.0
        return (ppo2_limit / self.f_o2 - 1.0) * 10.0


@dataclass
class WaypointInput:    # zadany bod profilu
    seq_num: int       # poradove cislo (1, 2, 3...)
    depth_m: float     # cilova hloubka v metrech
    time_min: float    # cas v hloubce [min]
    tank_name: str     # odpovida TankInput.tank_name


# TRIDY OUTPUT DAT

@dataclass
class ProfileRow:
    # jeden segment profilu 
    segment_id: int
    seg_type: str        # "descent" | "bottom" | "ascent" | "deco_stop"
    from_depth: float    # [m] vystup se prevadi do preferovane jednotky
    to_depth: float      # [m]
    duration_min: float
    tank_name: str
    mix: str
    # (avg_depth, cns_segment_pct, otu_segment) interni nejsou v API odpovedi
    avg_depth: float
    cns_segment_pct: float
    otu_segment: float


@dataclass
class TankGasInfo:  # prehled spotreby dane lahve
    tank_name: str
    mix: str
    gas_sum_l: float     # celkovy plyn [l]
    usable_l: float      # pouzitelny plyn bez zalohy [l]
    backup_l: float      # zalozni rezerva [l]
    consumed_l: float    # spotreba behem ponoru [l]
    remaining_l: float   # zbyvajici plyn = gas_sum_l - consumed_l [l]


@dataclass
class PlanSummary:      # celkovy souhrn ponoru
    total_time_min: float
    avg_depth_m: float
    max_depth_m: float
    ndl_min: Optional[int]
    is_deco: bool
    gas_sum_l: float         # celkovy plyn vsech lahvi [l]
    consumed_gas_l: float    # celkova spotreba [l]
    remaining_gas_l: float   # celkovy zustatek [l]
    tanks_gas: List[TankGasInfo]   # prehled na lahev
    cns_total_pct: float
    otu_total: float
    mods: Dict[str, float]   # tank_name -> MOD [m]
    deco_source: str
    warnings: List[str]


@dataclass
class PlanResult:   # vysledek planovace
    profile: List[ProfileRow]
    deco_stops: List[Dict[str, Any]]   # [{stop_depth_m, duration_min, tank_name, mix}]
    summary: PlanSummary


# Pomocne fce

def _ata(depth_m: float) -> float:  # Absolutni tlak ATA pro danou hloubku (ATA = depth/10 +1)
    return depth_m / 10.0 + 1.0


def _seg_cns_pct(f_o2: float, avg_depth_m: float, duration_min: float) -> float:
    pp = round(f_o2 * _ata(avg_depth_m), 3)    # CNS pro segment (ppO2 = FO2 * ATA) MBT z NOAA table -> (CNS = [duration / MBT] * 100)
    if pp < 0.6:            # pod prahem CNS toxicity
        return 0.0
    mbt = _ceiling_mbt(pp)
    if mbt <= 0.0:
        return 0.0
    return (duration_min / mbt) * 100.0


def _seg_otu(f_o2: float, avg_depth_m: float, duration_min: float) -> float:
    pp = f_o2 * _ata(avg_depth_m)    # OTU pro segment kdy pod 0.5 ATA ppO2 je OTU = 0 (sdili fci calc_otu z otu)
    if pp <= 0.5:
        return 0.0
    try:
        return float(calc_otu(pp_o2_ata=pp, time_min=duration_min))
    except Exception:
        return 0.0


def _seg_gas_l(sac_l_min: float, avg_depth_m: float, duration_min: float) -> float:
    return sac_l_min * _ata(avg_depth_m) * duration_min    # spotreba plynu segmentu v [l] (gas = SAC * ATA * cas)


def _make_segment(
    seg_id: int,
    seg_type: str,
    from_d: float,
    to_d: float,
    duration: float,
    tank: TankInput,
    avg_d: float,
) -> ProfileRow:    # na ProfileRow, zkracuje opakovani
    return ProfileRow(
        segment_id=seg_id,
        seg_type=seg_type,
        from_depth=round(from_d, 1),
        to_depth=round(to_d, 1),
        duration_min=round(duration, 2),
        tank_name=tank.tank_name,
        mix=tank.mix_label,
        avg_depth=round(avg_d, 1),
        cns_segment_pct=round(_seg_cns_pct(tank.f_o2, avg_d, duration), 2),
        otu_segment=round(_seg_otu(tank.f_o2, avg_d, duration), 2),
    )


# MAIN FCE

def plan_dive_profile(
    *,
    sac_l_min: float,
    tanks: List[TankInput],
    waypoints: List[WaypointInput],
    allow_deco: bool = True,
    ppo2_limit: float = 1.6,
    descent_rate_m_min: float = 10.0,
    ascent_rate_m_min: float = 10.0,
) -> PlanResult:        # Sestavi profil z waypointu dle seq_num (resi allow_deto True/False)

    # ----- 1. VALIDACE -----
    if not tanks:
        raise ValueError("Musi byt zadana alespon jedna lahev.")
    if not waypoints:
        raise ValueError("Musi byt zadan alespon jeden waypoint.")
    if sac_l_min <= 0:
        raise ValueError("SAC musi byt > 0 l/min.")
    if descent_rate_m_min <= 0 or ascent_rate_m_min <= 0:
        raise ValueError("Rychlosti klesani a stoupani musi byt > 0 m/min.")

    # Sestavime mapu lahev pro O(1) lookup dle jmena
    tank_map: Dict[str, TankInput] = {t.tank_name: t for t in tanks}
    if len(tank_map) < len(tanks):
        raise ValueError("Kazda lahev musi mit jedinecny tank_name.")

    warnings: List[str] = []
    profile: List[ProfileRow] = []
    seg_id = 1
    current_depth = 0.0

    # ----- 2. Serazeni waypointu dle poradi -----
    sorted_waypoints = sorted(waypoints, key=lambda w: w.seq_num)

    # ----- 3. Sestaveni segmentu profilu (klesani + dno) -----
    for wp in sorted_waypoints:
        tank = tank_map.get(wp.tank_name)
        if tank is None:
            raise ValueError(
                f"Waypoint seq_num={wp.seq_num} odkazuje na neexistujici lahev "
                f"'{wp.tank_name}'. Dostupne: {sorted(tank_map.keys())}."
            )

        if abs(wp.depth_m - current_depth) > 0.01:          # Prechod hloubky (klesani nebo stoupani mezi waypointy)
            if wp.depth_m > current_depth:
                seg_type = "descent"
                t_time = (wp.depth_m - current_depth) / descent_rate_m_min
            else:
                seg_type = "ascent"
                t_time = (current_depth - wp.depth_m) / ascent_rate_m_min
            avg_d = (current_depth + wp.depth_m) / 2.0              # Prumerna hloubka segmentu = stred intervalu
            profile.append(_make_segment(seg_id, seg_type, current_depth, wp.depth_m, t_time, tank, avg_d))
            seg_id += 1

        if wp.time_min > 0:         # Cas na dne v cilove hloubce
            profile.append(_make_segment(seg_id, "bottom", wp.depth_m, wp.depth_m, wp.time_min, tank, wp.depth_m))
            seg_id += 1

        current_depth = wp.depth_m

    # ----- 4. NDL/deko plan z tabulek -----
    max_depth_m = max(wp.depth_m for wp in sorted_waypoints)     # Celkovy cas do zacatku vystupu = souhrn vsech segmentu dosud
    time_to_ascent = sum(row.duration_min for row in profile)

    
    deepest_wp = max(sorted_waypoints, key=lambda w: w.depth_m) # Pouzijeme plyn z nejhlubsiho waypointu
    deepest_tank = tank_map.get(deepest_wp.tank_name, tanks[0])

    deco_plan = plan_dive(
        depth_m=max_depth_m,
        bottom_time_min=time_to_ascent,
        f_o2=deepest_tank.f_o2,
    )
    ndl_min: Optional[int] = deco_plan.get("ndl")
    is_deco: bool = bool(deco_plan.get("is_deco", False))
    stops_raw: List[Tuple[int, int]] = deco_plan.get("stops", [])
    deco_source: str = deco_plan.get("source", "fallback")

    # ----- 5. Stoupani respektuje allow_deco -----
    last_tank = tank_map.get(sorted_waypoints[-1].tank_name, tanks[0])
    deco_stops_out: List[Dict[str, Any]] = []

    # NDL rezim: pokud ponor prekracuje NDL -- varovat a ignorovat zastavky
    if not allow_deco and is_deco:
        effective_stops: List[Tuple[int, int]] = []
        warnings.append(
            f"Ponor prekracuje bezdekompresni limit! "
            f"NDL pro hloubku {max_depth_m} m: {ndl_min} min. "
            f"Pro NDL ponor zkratte celkovy cas pod vodou na maximalne {ndl_min} min."
        )
    else:
        # Zastavky razeny od nejhlubsi k hladine (sestupne dle hloubky)
        effective_stops = sorted(stops_raw, key=lambda s: -float(s[0]))

    if effective_stops:
        prev_depth = current_depth
        for (stop_d, stop_min) in effective_stops:
            stop_d_m = float(stop_d)
            stop_dur_min = float(stop_min)

            # Stoupani k zastavce
            if prev_depth > stop_d_m + 0.01:
                asc_time = (prev_depth - stop_d_m) / ascent_rate_m_min
                avg_d = (prev_depth + stop_d_m) / 2.0
                profile.append(_make_segment(seg_id, "ascent", prev_depth, stop_d_m, asc_time, last_tank, avg_d))
                seg_id += 1

            # Deko zastavka
            profile.append(_make_segment(seg_id, "deco_stop", stop_d_m, stop_d_m, stop_dur_min, last_tank, stop_d_m))
            seg_id += 1

            deco_stops_out.append({
                "stop_depth_m": stop_d_m,
                "duration_min": stop_dur_min,
                "tank_name": last_tank.tank_name,
                "mix": last_tank.mix_label,
            })
            prev_depth = stop_d_m

        if prev_depth > 0.01:           # Stoupani od posledni zastavky na hladinu
            asc_time = prev_depth / ascent_rate_m_min
            avg_d = prev_depth / 2.0
            profile.append(_make_segment(seg_id, "ascent", prev_depth, 0.0, asc_time, last_tank, avg_d))
            seg_id += 1

    else:
        if current_depth > 0.01:        # Prime stoupani na hladinu (bez zastavek)
            asc_time = current_depth / ascent_rate_m_min
            avg_d = current_depth / 2.0
            profile.append(_make_segment(seg_id, "ascent", current_depth, 0.0, asc_time, last_tank, avg_d))
            seg_id += 1

    # ----- 6. Celkove statistiky -----
    total_time_min = round(sum(row.duration_min for row in profile), 1)

    if total_time_min > 0:         # Vazeny prumer hloubky -- vahy jsou delky segmentu
        avg_depth_m = sum(row.avg_depth * row.duration_min for row in profile) / total_time_min
    else:
        avg_depth_m = 0.0

    tank_consumed: Dict[str, float] = {}    # Spotreba plynu na lahev (vsechny segmenty)
    for row in profile:
        gas = _seg_gas_l(sac_l_min, row.avg_depth, row.duration_min)
        tank_consumed[row.tank_name] = tank_consumed.get(row.tank_name, 0.0) + gas

    gas_sum_l = sum(t.gas_sum_l for t in tanks)
    consumed_gas_l = sum(tank_consumed.values())
    remaining_gas_l = gas_sum_l - consumed_gas_l

    cns_total_pct = round(sum(row.cns_segment_pct for row in profile), 1)
    otu_total = round(sum(row.otu_segment for row in profile), 1)

    tanks_gas: List[TankGasInfo] = []       # Prehled na lahev + backup varovani pri zasahu do rezervy
    for t in tanks:
        consumed = tank_consumed.get(t.tank_name, 0.0)
        tanks_gas.append(TankGasInfo(
            tank_name=t.tank_name,
            mix=t.mix_label,
            gas_sum_l=round(t.gas_sum_l, 0),
            usable_l=round(t.usable_gas_l, 0),
            backup_l=round(t.backup_gas_l, 0),
            consumed_l=round(consumed, 0),
            remaining_l=round(t.gas_sum_l - consumed, 0),
        ))
        if consumed > t.usable_gas_l + 0.5:         # Spotreba zasahuje do bezpecnostni rezervy
            warnings.append(
                f"Lahev '{t.tank_name}' ({t.mix_label}): spotreba {round(consumed, 0):.0f} l "
                f"zasahuje do bezpecnostni rezervy {round(t.backup_gas_l, 0):.0f} l "
                f"(pouzitelny plyn bez rezervy: {round(t.usable_gas_l, 0):.0f} l)!"
            )

    # MOD pro kazdou lahev [m] pri zadanem ppO2 limitu
    mods: Dict[str, float] = {
        t.tank_name: round(t.mod_m(ppo2_limit), 1) for t in tanks
    }

    # ----- 7. Varovani -----
    if consumed_gas_l > gas_sum_l:
        warnings.append(
            f"Celkova spotreba plynu ({round(consumed_gas_l, 0):.0f} l) prekracuje "
            f"celkovou zasobu ({round(gas_sum_l, 0):.0f} l)!"
        )
    if cns_total_pct > 80.0:
        warnings.append(
            f"Celkovy CNS {cns_total_pct} % prekracuje doporuceny limit 80 %. "
            "Po ponoru je nutna pauza."
        )
    if otu_total > 300.0:
        warnings.append(f"Celkovy OTU {otu_total} prekracuje denni limit 300 OTU.")

    # MOD varovani pro kazdy waypoint (kontrola hloubky vuci MOD lahve)
    for wp in sorted_waypoints:
        tank = tank_map.get(wp.tank_name, tanks[0])
        mod = tank.mod_m(ppo2_limit)
        if wp.depth_m > mod + 0.01:
            warnings.append(
                f"Waypoint #{wp.seq_num}: hloubka {wp.depth_m} m prekracuje MOD "
                f"pro lahev '{wp.tank_name}' ({tank.mix_label}). "
                f"Maximalni bezpecna hloubka: {round(mod, 1)} m "
                f"(ppO2 limit {ppo2_limit} ATA)."
            )

    summary = PlanSummary(
        total_time_min=total_time_min,
        avg_depth_m=round(avg_depth_m, 1),
        max_depth_m=max_depth_m,
        ndl_min=ndl_min,
        is_deco=is_deco,
        gas_sum_l=round(gas_sum_l, 0),
        consumed_gas_l=round(consumed_gas_l, 0),
        remaining_gas_l=round(remaining_gas_l, 0),
        tanks_gas=tanks_gas,
        cns_total_pct=cns_total_pct,
        otu_total=otu_total,
        mods=mods,
        deco_source=deco_source,
        warnings=warnings,
    )

    return PlanResult(
        profile=profile,
        deco_stops=deco_stops_out,
        summary=summary,
    )
