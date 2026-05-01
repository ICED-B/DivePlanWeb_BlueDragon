from __future__ import annotations
# SAC (Surface Air COnsumption) & RMV (Respiratory Minute Volume)
# pokryva vazeny prumer ATA pres vice segmentu, vypocet SAC ze spotreby, primy vypocet a prevod poklesu na objem spotreby

from app.planner.core.types import Segment, PlannerServiceError
from app.services.gas_service import ata_at_depth
from app.utils.enums import DepthUnitEnum


def weighted_ata_for_segments(segments: list[Segment]) -> float:
    # vazeny prumer ATA pres all segments profilu
    # avg_ATA = sum(ATA_i * t_i) / sum(t_i)
    if not segments:
        raise PlannerServiceError("Chybi segmenty profilu.")

    total_time = sum(float(s.duration_min) for s in segments)
    if total_time <= 0:
        raise PlannerServiceError("Soucet casu segmentu musi byt kladny.")

    weighted = 0.0
    for s in segments:
        weighted += float(ata_at_depth(float(s.avg_depth),          # ATA pro prumernou hloubku segmentu
                          s.depth_unit)) * float(s.duration_min)

    return round(weighted / total_time, 3)


def sac_from_consumption(gas_used_l: float, total_time_min: float, avg_ata: float) -> float:    # vypocet SAC/RMV ze spotreby plynu, [SAC = gas_used_l / (total_time_min * avg_ATA)]
    if gas_used_l <= 0:
        raise PlannerServiceError("gas_used_l musi byt > 0.")
    if total_time_min <= 0:
        raise PlannerServiceError("total_time_min musi byt > 0.")
    if avg_ata <= 0:
        raise PlannerServiceError("avg_ata musi byt > 0.")

    sac = float(gas_used_l) / (float(total_time_min) * float(avg_ata))
    return round(sac, 2)


def calc_rmv(
    *,
    depth: float,
    tank_volume_l: float,
    pressure_drop_bar: float,
    time_min: float,
    depth_unit: DepthUnitEnum = DepthUnitEnum.METERS,
) -> float:
    # vypocita RMV v l/min kdy [gas_used_l = tank_volume_l * pressure_drop_bar], [RMV = gas_used_l / (time_min * ATA(depth))]
    if tank_volume_l <= 0:
        raise ValueError("tank_volume_l musi byt > 0.")
    if pressure_drop_bar <= 0:
        raise ValueError("pressure_drop_bar musi byt > 0.")
    if time_min <= 0:
        raise ValueError("time_min musi byt > 0.")
    gas_used_l = tank_volume_l * pressure_drop_bar    # Celkovy spotrebovany plyn z tlakoveho poklesu lahve
    ata = float(ata_at_depth(depth, depth_unit))
    return round(gas_used_l / (time_min * ata), 2)


def calc_sac_bar_min(
    *,
    depth: float,
    pressure_drop_bar: float,
    time_min: float,
    depth_unit: DepthUnitEnum = DepthUnitEnum.METERS,
) -> float:
    # SAC v bar/min kdy [SAC = pressure_drop_bar / (time_min * ATA(depth))]
    if pressure_drop_bar <= 0:
        raise ValueError("pressure_drop_bar musi byt > 0.")
    if time_min <= 0:
        raise ValueError("time_min musi byt > 0.")
    ata = float(ata_at_depth(depth, depth_unit))
    return round(pressure_drop_bar / (time_min * ata), 3)


def gas_used_l_from_tank_drop(
    *,
    tank_volume_l: float,
    start_pressure_bar: float,
    end_pressure_bar: float,
) -> float:
    # prevod tlakoveho poklesu lahve na spotrebovany objem plynu v [l] | [gas_used_l = tank_volume_l * (start_pressure - end_pressure)]
    if tank_volume_l <= 0:
        raise PlannerServiceError("tank_volume_l musi byt > 0.")
    if start_pressure_bar < 0 or end_pressure_bar < 0:
        raise PlannerServiceError("Tlak musi byt >= 0.")
    drop = float(start_pressure_bar) - float(end_pressure_bar)
    if drop <= 0:
        raise PlannerServiceError("Pokles tlaku musi byt > 0.")

    return round(float(tank_volume_l) * drop, 1)
