from __future__ import annotations
# MOD (maximum Operating Depth) jedna se o max hloubku ve ktere bezpecne pouzti smes pro dane ppO2
# MOD = (ppO2_limit / FO2 - 1) * 10 [metry]

from app.utils.enums import DepthUnitEnum
from app.services.gas_service import mod


def calc_mod(
    *,
    f_o2: float,
    max_pp_o2: float = 1.4,
    depth_unit: DepthUnitEnum = DepthUnitEnum.METERS,
) -> float:
    # param f_o2, max_pp_o2, depth_unit
    if not (0.0 < f_o2 <= 1.0):
        raise ValueError("f_o2 musi byt v intervalu (0, 1].")
    if max_pp_o2 <= 0:
        raise ValueError("max_pp_o2 musi byt > 0.")
    return round(float(mod(f_o2, max_pp_o2, depth_unit)), 1)
