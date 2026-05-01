from __future__ import annotations
# vlastnosti potapecskych smesi v dane hloubce
# hustota smesi, END a vlastnosti pro API endpoint
from typing import Dict, Any

from app.utils.enums import DepthUnitEnum
from app.utils.units import convert_depth
from app.planner.core.types import Number


# Hustoty cistych plynu pri ~1 bar a 0-15 degC (hrube aproximace)
_DENSITY_O2_SURFACE = 1.429  # g/L
_DENSITY_N2_SURFACE = 1.251  # g/L
_DENSITY_HE_SURFACE = 0.1785  # g/L


def _depth_m(depth: Number, unit: DepthUnitEnum) -> float:  # prevod hloubky na metry
    return float(convert_depth(depth, unit, DepthUnitEnum.METERS))


def _p_abs(depth_m: float) -> float:    # absolutni tlak v bar/ATA (1 bar na hladine + 1bar / 10m)
    return 1.0 + depth_m / 10.0


def gas_density_at_depth(
    f_o2: float,
    f_he: float,
    depth: Number,
    unit: DepthUnitEnum,
) -> float:
    # priblizna hustota smesi v g/L pri dane hloubce
    f_o2 = float(f_o2)
    f_he = float(f_he)
    # f_n2 = max(0.0, 1.0 - f_o2 - f_he)
    f_o2 = float(f_o2)
    f_he = float(f_he)
    if f_o2 < 0 or f_he < 0 or f_o2 + f_he > 1.0:
        raise ValueError(
            "Neplatne frakce: FO2 a FHe musi byt >=0 a FO2+FHe <= 1.")
    f_n2 = 1.0 - f_o2 - f_he

    # Hustota smesi na povrchu, vazeny prumer
    density_surface = (
        f_o2 * _DENSITY_O2_SURFACE +
        f_he * _DENSITY_HE_SURFACE +
        f_n2 * _DENSITY_N2_SURFACE
    )

    depth_m = _depth_m(depth, unit)
    p = _p_abs(depth_m)     # Hustota roste linearane s tlakem (predpoklad idealniho plynu)
    return density_surface * p


def end_for_mix(
    depth: Number,
    unit: DepthUnitEnum,
    f_o2: float,
    f_he: float,
) -> float:
    # equivalent narcotic Depth kdy O2 i N2 jsou narkoticke
    depth_m = _depth_m(depth, unit)
    fn2_air = 0.79  # podil N2 ve vzduchu, reference pro narkoticky efekt
    f_n2 = max(0.0, 1.0 - float(f_o2) - float(f_he))
    narcotic_fraction = f_n2 + float(f_o2)    # Soucet narkotickych frakcii (O2 + N2, bez He)
    end_m = ((narcotic_fraction / fn2_air) * (depth_m + 10.0)) - 10.0
    return float(convert_depth(end_m, DepthUnitEnum.METERS, unit))    # Prevod vysledku zpet do pozadovane jednotky


def gas_properties_summary(
    depth: Number,
    unit: DepthUnitEnum,
    f_o2: float,
    f_he: float,
) -> Dict[str, Any]:
    # vraci vlastnosti  smesi v dane hloubce
    depth_m = _depth_m(depth, unit)
    density = gas_density_at_depth(f_o2, f_he, depth, unit)
    end_depth = end_for_mix(depth, unit, f_o2, f_he)

    return {
        "depth": float(depth),
        "depth_unit": unit.value,
        "fo2": float(f_o2),
        "fhe": float(f_he),
        "fn2": max(0.0, 1.0 - float(f_o2) - float(f_he)),
        "density_g_l": density,
        "end": end_depth,
        "end_unit": unit.value,
        "p_abs": _p_abs(depth_m),
    }
