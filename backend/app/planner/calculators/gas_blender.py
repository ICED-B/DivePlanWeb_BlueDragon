from __future__ import annotations
# michani nitroxu metodou partial-pressure
# lahev na tlaku P_start s pocatecni smesi FO2_start -> pridame cisty O2 -> dofoukneme vzduchem do vysledneho tlaku

from typing import Dict, Any

from app.planner.core.types import Number


def blend_nitrox_partial_pressure(
    start_pressure_bar: Number,
    start_fo2: float,
    final_pressure_bar: Number,
    target_fo2: float,
) -> Dict[str, Any]:

    P_start = float(start_pressure_bar)
    P_final = float(final_pressure_bar)
    FO2_start = float(start_fo2)
    FO2_target = float(target_fo2)

    if P_final <= P_start:
        raise ValueError("Konecny tlak musi byt vyssi nez pocatecni.")
    if not (0.0 < FO2_target < 1.0):
        raise ValueError("target_fo2 musi byt mezi 0 a 1.")
    if not (0.0 <= FO2_start < 1.0):
        raise ValueError("start_fo2 musi byt mezi 0 a 1.")

    # Existujici mnozstvi O2 v lahvi (bar * FO2)
    A = FO2_start * P_start
    # Citatel reseni rovnice -- viz komentar v docstringu
    numerator = P_final * FO2_target - A + P_start - 0.21 * P_final
    denom = 0.79  # 1.0 - 0.21 (podil N2 ve vzduchu)

    # Tlak po pridani O2 (pred dofoukanim vzduchem)
    P1 = numerator / denom

    if not (P_start <= P1 <= P_final):
        # Teoreticky neproveditelne, napr pro prilis vysoka pozadovana FO2
        raise ValueError("Nelze dosahnout pozadovane FO2 danou metodou a tlaky.")

    o2_bar_to_add = P1 - P_start
    air_bar_to_add = P_final - P1

    # Overovaci vypocet vysledne FO2 (pro jistotu)
    o2_final = (A + o2_bar_to_add + 0.21 * air_bar_to_add) / P_final

    return {
        "start_pressure_bar": P_start,
        "start_fo2": FO2_start,
        "final_pressure_bar": P_final,
        "target_fo2": FO2_target,
        "o2_bar_to_add": o2_bar_to_add,
        "air_bar_to_add": air_bar_to_add,
        "result_fo2_check": o2_final,  # kontrolni hodnota, mela by odpovidat target_fo2
    }
