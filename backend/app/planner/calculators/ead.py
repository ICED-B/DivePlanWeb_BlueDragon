from __future__ import annotations
# EAD (Equivalent Air Depth) pro nitrox
# EAD je hloubka ve ktere by mel vzduch stejny parcialni tlak dusiku jako pouzivany nitrox v realne hloubce
# EAD = ((FN2 / 0.79) * (depth + 10)) - 10   [metry]

from app.utils.enums import DepthUnitEnum
from app.services.gas_service import ead_nitrox
from app.planner.calculators.validators import fraction01, non_negative


def calc_ead(
    *,
    depth: float,
    f_o2: float,
    depth_unit: DepthUnitEnum = DepthUnitEnum.METERS,
) -> float:
    # param (depth, f_o2, depth_unit)
    # fraction01 akceptuje 0.32 nebo 32 (procenta -> automaticky prevede)
    f = fraction01(f_o2, "f_o2", min_value=0.0)
    d = non_negative(depth, "depth")
    return round(float(ead_nitrox(d, f, depth_unit)), 1)
