from __future__ import annotations
# END (Equivalent Narcotic Depth) pro smesi s heliem
# END je hloubka ve ktere by mel vzduch stejny narkoticky efekt jako pouzivana smes v realne hloubce
# narcotic_fraction = FO2 + FN2 = FO2 + (1 - FO2 - FHe)
# END = ((narcotic_fraction / 0.79) * (depth + 10)) - 10 [metry]

from app.utils.enums import DepthUnitEnum
from app.services.gas_service import end_trimix


def calc_end(
    *,
    depth: float,
    f_o2: float,
    f_he: float = 0.0,
    depth_unit: DepthUnitEnum = DepthUnitEnum.METERS,
) -> float:
    # param (depth, f_o2, f_he, depth_unit), ValueError pri neplatnych frakcich (soucet FO2+FHe > 1)
    if not (0.0 < f_o2 <= 1.0):
        raise ValueError("f_o2 musi byt v intervalu (0, 1].")
    if not (0.0 <= f_he <= 1.0):
        raise ValueError("f_he musi byt v intervalu [0, 1].")
    if f_o2 + f_he > 1.0:
        raise ValueError("Soucet f_o2 + f_he nesmi presahnout 1.0.")
    return round(float(end_trimix(depth, f_o2, f_he, depth_unit)), 1)
