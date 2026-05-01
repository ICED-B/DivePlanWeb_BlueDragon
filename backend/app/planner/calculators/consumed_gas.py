from __future__ import annotations
# spotreba plynu pro segment
# [consumed_L = RMV * ATA(detph) * time] | [consumed_bar = consumed_L / tank_volume_L]

from dataclasses import dataclass
from app.utils.enums import DepthUnitEnum
from app.services.gas_service import ata_at_depth


@dataclass(frozen=True)
class ConsumedGasResult:    # vysledek vypoctu
    consumed_l: float    # spotreba v litrech (povrchovy objem)
    consumed_bar: float  # spotreba v barech (pro danou lahev)


def calc_consumed_gas(
    *,
    rmv_l_min: float,
    depth: float,
    time_min: float,
    tank_volume_l: float,
    depth_unit: DepthUnitEnum = DepthUnitEnum.METERS,
) -> ConsumedGasResult:
    # pocita spotrebovany plyn za dany cas v dane hloubce
    # param (rmv_l_min, depth, time_min, tank_volume_l, depth_unit)
    if rmv_l_min <= 0:
        raise ValueError("rmv_l_min musi byt > 0.")
    if time_min <= 0:
        raise ValueError("time_min musi byt > 0.")
    if tank_volume_l <= 0:
        raise ValueError("tank_volume_l musi byt > 0.")

    # Absolutni tlak v ATA pro danou hloubku
    ata = float(ata_at_depth(depth, depth_unit))
    consumed_l = rmv_l_min * ata * time_min
    # Prepocet na bary: tlakovy pokles = obj. spotreba / geometr. objem lahve
    consumed_bar = consumed_l / tank_volume_l

    return ConsumedGasResult(
        consumed_l=round(float(consumed_l), 1),
        consumed_bar=round(float(consumed_bar), 1),
    )
