from __future__ import annotations
# best_mix pro danou hloubku
# best_mix = FO2 = ppO2_target / ATA(depth) [interval 0,1 na 3 desetinna]

from app.utils.enums import DepthUnitEnum
from app.services.gas_service import best_mix
from app.planner.calculators.validators import non_negative, positive


def calc_best_mix(
    *,
    depth: float,
    target_pp_o2: float = 1.4,
    depth_unit: DepthUnitEnum = DepthUnitEnum.METERS,
) -> float:
    # vraci optimalni FO2 (frakce) pro pozadovane ppO2
    # param (depth, target_pp_o2, depth_unit)
    d = non_negative(depth, "depth")
    p = positive(target_pp_o2, "target_pp_o2")
    # Na gas_service, ktery zvlada prevod jednotek
    return round(float(best_mix(d, target_pp_o2=p, unit=depth_unit)), 3)
