from __future__ import annotations
# maximalni doba ponoru pri dane zasobe plynu
# usable_gas_L = RMV * ATA(depth) * time    | [time = usable_gas_L / (RMV * ATA)]

from app.utils.enums import DepthUnitEnum
from app.services.gas_service import ata_at_depth


def calc_dive_time_from_tank(
    *,
    depth: float,
    tank_volume_l: float,
    pressure_available_bar: float,
    rmv_l_min: float,
    depth_unit: DepthUnitEnum = DepthUnitEnum.METERS,
) -> float:
    # max cas v hloubce pro danou zasobu plynu v lahvi
    # param (tank_volume_l, pressure_available_bar, rmv_l_min)
    if tank_volume_l <= 0:
        raise ValueError("tank_volume_l musi byt > 0.")
    if pressure_available_bar <= 0:
        raise ValueError("pressure_available_bar musi byt > 0.")
    if rmv_l_min <= 0:
        raise ValueError("rmv_l_min musi byt > 0.")

    # Celkovy dostupny plyn = objem lahve * dostupny tlak
    usable_gas_l = tank_volume_l * pressure_available_bar
    ata = float(ata_at_depth(depth, depth_unit))
    return round(usable_gas_l / (rmv_l_min * ata), 1)


def calc_dive_time_min(
    *,
    rmv_l_min: float,
    depth: float,
    usable_gas_l: float,
    depth_unit: DepthUnitEnum = DepthUnitEnum.METERS,
) -> float:
    # max cas ponoru z objemu dostupneho plynu v litrech    [time = usable_gas_L / (RMV * ATA(depth))]
    if rmv_l_min <= 0:
        raise ValueError("rmv_l_min musi byt > 0.")
    if usable_gas_l <= 0:
        raise ValueError("usable_gas_l musi byt > 0.")
    ata = float(ata_at_depth(depth, depth_unit))
    t = usable_gas_l / (rmv_l_min * ata)
    return round(float(t), 1)
