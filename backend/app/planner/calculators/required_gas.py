from __future__ import annotations
# pozadovane mnozstvi plynu v [l] pro dany segment
# required_L = RMV * ATA(depth) * time_min      |  RMV (respiracni minutovy objem) [l/min]

from app.utils.enums import DepthUnitEnum
from app.services.gas_service import ata_at_depth


def calc_required_gas_liters(
    *,
    rmv_l_min: float,
    depth: float,
    time_min: float,
    depth_unit: DepthUnitEnum = DepthUnitEnum.METERS,
) -> float:
    # min potrebny povrchovy objem plynu, (required_L = RMV * ATA(depth) * time_min)
    if rmv_l_min <= 0:
        raise ValueError("rmv_l_min musi byt > 0.")
    if time_min <= 0:
        raise ValueError("time_min musi byt > 0.")
    ata = float(ata_at_depth(depth, depth_unit))        # Absolutni tlak v ATA pro danou hloubku
    required = rmv_l_min * ata * time_min
    return round(float(required), 1)
