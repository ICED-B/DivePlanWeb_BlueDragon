from __future__ import annotations
# ppO2 (parcialni tlak kyslíku) pro danou smes a hloubku
# ppO2 = FO2 * ATA(depth) | ATA = depth_m / 10 + 1
from app.utils.enums import DepthUnitEnum
from app.services.gas_service import pp_o2
from app.planner.calculators.validators import fraction01, non_negative


def calc_ppo2(
    *,
    f_o2: float,
    depth: float,
    depth_unit: DepthUnitEnum = DepthUnitEnum.METERS,
) -> float:

    # vypocte parcialni tlak kysliku pro danou smes a hloubku, normalizuje vstup -- 21 -> 0.21, 0.21 -> 0.21
    f = fraction01(f_o2, "f_o2", min_value=0.0)
    d = non_negative(depth, "depth")
    return round(float(pp_o2(f, d, depth_unit)), 3)
