# nitrox souhrn kalkulaci, spoji ppO2, MOD, best mix a EAD do jednoho volani
from __future__ import annotations

from dataclasses import dataclass

from app.utils.enums import DepthUnitEnum
from app.services.gas_service import pp_o2, mod, best_mix, ead_nitrox


@dataclass(frozen=True)
class NitroxSummary:
    depth: float
    depth_unit: DepthUnitEnum
    f_o2: float
    max_pp_o2: float
    pp_o2_ata: float
    mod_depth: float
    best_mix_f_o2: float
    ead_depth: float


def nitrox_summary(
    *,
    depth: float,
    unit: DepthUnitEnum = DepthUnitEnum.METERS,
    f_o2: float,
    max_pp_o2: float = 1.4,
    target_pp_o2: float | None = None,
) -> dict:
    # souhrn nitrox, vraci ppO2, MOD, FO2, best_mix, EAD pro hloubku a smes
    if not (0.0 < f_o2 <= 1.0):
        raise ValueError("f_o2 musí být v intervalu (0, 1].")
    if max_pp_o2 <= 0:
        raise ValueError("max_pp_o2 musí být > 0.")

    # Pokud neni zadano cílové ppO2 pro best mix, pouzijeme max_pp_o2
    if target_pp_o2 is None:
        target_pp_o2 = max_pp_o2

    ppo2 = float(pp_o2(f_o2, depth, unit))
    mod_depth = float(mod(f_o2, max_pp_o2, unit))
    bm = float(best_mix(depth, target_pp_o2=target_pp_o2, unit=unit))
    ead = float(ead_nitrox(depth, f_o2, unit))

    return {
        "depth": float(depth),
        "depth_unit": unit.value,
        "f_o2": round(float(f_o2), 3),
        "max_pp_o2": round(float(max_pp_o2), 2),
        "pp_o2_ata": round(ppo2, 3),
        "mod": round(mod_depth, 1),
        "best_mix_f_o2": round(bm, 3),
        "ead": round(ead, 1),
    }
