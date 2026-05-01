from __future__ import annotations

def calc_tank_gas_content_liters(*, tank_volume_l: float, pressure_bar: float) -> float:
    # mnozstvi plynu prepoctene na 1 bar (surface liters) = objem_lahve_l * tlak_bar
    if tank_volume_l <= 0:
        raise ValueError("tank_volume_l musí být > 0.")
    if pressure_bar < 0:
        raise ValueError("pressure_bar musí být >= 0.")
    return round(float(tank_volume_l * pressure_bar), 1)
