# backend/app/planner/calculators/gas_reserves.py
from __future__ import annotations
# rezervy a min zasoby plynu
# prepocet objemu plynu z poklesu, celkovy objem, min zalozni rezerva, pozadovany pocatecni tlak

from dataclasses import dataclass

from app.planner.core.types import PlannerServiceError, Segment, TankSpec
from app.services.gas_service import ata_at_depth


def gas_used_l_from_pressure_drop(*, tank_volume_l: float, pressure_drop_bar: float) -> float:  # ovjem plynu z poklesu (gas_l = tank_volume_l * pressure_drop_bar)
    if tank_volume_l <= 0:
        raise PlannerServiceError("tank_volume_l musi byt > 0.")
    if pressure_drop_bar <= 0:
        raise PlannerServiceError("pressure_drop_bar musi byt > 0.")
    return round(float(tank_volume_l) * float(pressure_drop_bar), 1)


def pressure_drop_bar_from_gas_used(*, tank_volume_l: float, gas_used_l: float) -> float:   # tlakovy pokles z spotrebovaneho objemu (pressure_drop = gas_used_l / tank_volume_l)
    if tank_volume_l <= 0:
        raise PlannerServiceError("tank_volume_l musi byt > 0.")
    if gas_used_l <= 0:
        raise PlannerServiceError("gas_used_l musi byt > 0.")
    return round(float(gas_used_l) / float(tank_volume_l), 1)


def gas_needed_for_profile(*, rmv_l_min: float, segments: list[Segment]) -> float:  # potrebny plyn pro profil, [sum(RMV * ATA(segment.avg_depth) * segment.duration_min)] povrchovy
    if rmv_l_min <= 0:
        raise PlannerServiceError("rmv_l_min musi byt > 0.")
    if not segments:
        raise PlannerServiceError("Chybi segmenty profilu.")

    total = 0.0
    for s in segments:
        ata = float(ata_at_depth(float(s.avg_depth), s.depth_unit))        # ATA pro prumernou hloubku segmentu
        total += float(rmv_l_min) * ata * float(s.duration_min)

    return round(total, 1)


def rock_bottom_gas_l(
    *,
    depth_m: float,
    team_size: int = 2,
    sac_emergency_l_min: float = 20.0,
    ascent_rate_m_min: float = 10.0,
    safety_stop_min: float = 3.0,
    safety_stop_depth_m: float = 5.0,
) -> float:
    # minimalni zalozni rezerva plynu, (SAC_nouze * pocet_potapecu * (cas_na_dne + vystup + zastavka) * ATA(prumerna_hloubka))
    if depth_m < 0:
        raise PlannerServiceError("depth_m musi byt >= 0.")
    if team_size <= 0:
        raise PlannerServiceError("team_size musi byt > 0.")
    if sac_emergency_l_min <= 0:
        raise PlannerServiceError("sac_emergency_l_min musi byt > 0.")
    if ascent_rate_m_min <= 0:
        raise PlannerServiceError("ascent_rate_m_min musi byt > 0.")
    if safety_stop_min < 0:
        raise PlannerServiceError("safety_stop_min musi byt >= 0.")
    if safety_stop_depth_m < 0:
        raise PlannerServiceError("safety_stop_depth_m musi byt >= 0.")

    ascend_distance = max(0.0, float(depth_m) - float(safety_stop_depth_m))    # Vzdalenost vystupu od max hloubky k hloubce bezpecnostni zastavky
    t_ascent = ascend_distance / float(ascent_rate_m_min)

    avg_depth_ascent = (float(depth_m) + float(safety_stop_depth_m)) / 2.0    # Priblizna prumerna hloubka behem vystupu (stred intervalu)

    t_problem = 1.0    # 1 minuta reseni problemu v max. hloubce (bezna zjednodusujici konvence)

    gas_bottom = float(sac_emergency_l_min) * float(team_size) * \
        float(ata_at_depth(float(depth_m))) * t_problem
    gas_ascent = float(sac_emergency_l_min) * float(team_size) * \
        float(ata_at_depth(avg_depth_ascent)) * t_ascent
    gas_stop = float(sac_emergency_l_min) * float(team_size) * \
        float(ata_at_depth(float(safety_stop_depth_m))) * \
        float(safety_stop_min)

    return round(gas_bottom + gas_ascent + gas_stop, 1)


def start_pressure_required_bar(*, tank: TankSpec, planned_gas_l: float, reserve_gas_l: float) -> float:    # pocatecni tlak [(planned_gas_l + reserve_gas_l) / tank.volume_l]
    if planned_gas_l < 0 or reserve_gas_l < 0:
        raise PlannerServiceError(
            "planned_gas_l a reserve_gas_l musi byt >= 0.")
    if tank.volume_l <= 0:
        raise PlannerServiceError("tank.volume_l musi byt > 0.")

    total_needed_l = float(planned_gas_l) + float(reserve_gas_l)
    required_bar = total_needed_l / float(tank.volume_l)
    return round(min(required_bar, float(tank.working_pressure_bar)), 1)    # tlak lahve je maximum objemu
