# vypocty s plyny
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

from app.utils.enums import DepthUnitEnum
from app.utils.units import m_to_ft, ft_to_m


# Priblizne prepocty pro morskou vodu: 10 m ~ 1 ATA, 33 ft ~ 1 ATA
# ATA z hloubky: (hloubka / 10) + 1  [m]  nebo (hloubka / 33) + 1  [ft]

def ata_at_depth(depth: float, unit: DepthUnitEnum = DepthUnitEnum.METERS) -> float:
    # Absolutni tlak (ATA) v dane hloubce
    if unit == DepthUnitEnum.METERS:
        return depth / 10.0 + 1.0
    else:
        return depth / 33.0 + 1.0


def pp_o2(f_o2: float, depth: float, unit: DepthUnitEnum = DepthUnitEnum.METERS) -> float:
    # Parcialni tlak kysliku (ppO2) v ATA
    return f_o2 * ata_at_depth(depth, unit)


def mod(f_o2: float, max_pp_o2: float, unit: DepthUnitEnum = DepthUnitEnum.METERS) -> float:
    # Maximalni operacni hloubka (MOD) pro dane fO2 a ppO2
    # vzorec: (max_ppO2 / fO2 - 1) * 10  [m]  nebo * 33 [ft]
    if f_o2 <= 0:
        return 0.0
    if unit == DepthUnitEnum.METERS:
        return (max_pp_o2 / f_o2 - 1.0) * 10.0
    else:
        return (max_pp_o2 / f_o2 - 1.0) * 33.0


def best_mix(depth: float, target_pp_o2: float = 1.4, unit: DepthUnitEnum = DepthUnitEnum.METERS) -> float:
    # Best mix, doporuceny fO2 pro danou hloubku
    ata = ata_at_depth(depth, unit)
    f = target_pp_o2 / ata
    # Omezime do intervalu rozumnych hodnot (vzduch az cisty O2)
    return max(0.21, min(1.0, round(f, 3)))


# Ekvivalentni hloubky

def ead_nitrox(depth: float, f_o2: float, unit: DepthUnitEnum = DepthUnitEnum.METERS) -> float:
    # Equivalent Air Depth (EAD), hloubka vzduchu s obdobnym narkotickym ucinkem N2
    if unit == DepthUnitEnum.FEET:
        depth_m = ft_to_m(depth)
    else:
        depth_m = depth
    ead_m = ((depth_m + 10.0) * ((1.0 - f_o2) / 0.79)) - 10.0
    if unit == DepthUnitEnum.FEET:
        return m_to_ft(ead_m)
    return ead_m


def end_trimix(depth: float, f_o2: float, f_he: float, unit: DepthUnitEnum = DepthUnitEnum.METERS) -> float:
    # Ekvivalent Narcotic Depth (END) pro smesi s heliem, N2 jako hlavni narkoticky plyn
    # Zlomek dusiku: zbytek po O2 a He, minimalne 0
    f_n2 = max(0.0, 1.0 - f_o2 - f_he)
    if unit == DepthUnitEnum.FEET:
        depth_m = ft_to_m(depth)
    else:
        depth_m = depth
    end_m = ((depth_m + 10.0) * (f_n2 / 0.79)) - 10.0
    if unit == DepthUnitEnum.FEET:
        return m_to_ft(end_m)
    return end_m


# Smesovani plynu

@dataclass
class Mix:
    # zlomkove slozeni smesi (fO2, fHe, fN2 = zbytek)
    f_o2: float
    f_he: float = 0.0

    @property
    def f_n2(self) -> float:
        # Zlomek dusiku, vypocitany jako zbytek po O2 a He
        return max(0.0, 1.0 - self.f_o2 - self.f_he)


def topoff_nitrox(start: Mix, bank: Mix, start_pressure_bar: float, target_pressure_bar: float) -> Mix:
    # nove frakce po doplneni
    if target_pressure_bar <= 0 or target_pressure_bar < start_pressure_bar:
        return start
    p1 = max(0.0, start_pressure_bar)
    p2 = max(0.0, target_pressure_bar - p1)
    if p1 + p2 <= 0:
        return start

    # Vazeny prumer zlomku kysliku a helia dle castecnych tlaku
    f_o2 = (start.f_o2 * p1 + bank.f_o2 * p2) / (p1 + p2)
    f_he = (start.f_he * p1 + bank.f_he * p2) / (p1 + p2)
    # Normalizace numerickych chyb plovouci desetinne carky
    f_o2 = max(0.0, min(1.0, f_o2))
    f_he = max(0.0, min(1.0, f_he))
    return Mix(f_o2=f_o2, f_he=f_he)


def partial_pressure_blend_nitrox(
    target_f_o2: float,
    cylinder_pressure_bar: float,
    final_pressure_bar: float,
    oxygen_fill_bar: Optional[float] = None,
) -> Tuple[float, float]:

    # mix pro nitrox (O2 + vzduch)
    if not (0.21 <= target_f_o2 <= 1.0):
        raise ValueError("Cilovy fO2 musi byt v intervalu <0.21, 1.0>.")

    # Kolik baru je treba jeste dodat
    remaining = max(0.0, final_pressure_bar - cylinder_pressure_bar)
    if remaining <= 0:
        return 0.0, 0.0

    if oxygen_fill_bar is None:
        # Resime linearne: x + 0.21*(remaining - x) = target_fO2 * remaining  =>  x = remaining * (target - 0.21) / 0.79
        oxygen_to_add = remaining * (target_f_o2 - 0.21) / (1.0 - 0.21)
        oxygen_to_add = max(0.0, min(remaining, oxygen_to_add))
    else:
        # Pevne zadane mnozstvi O2, omezime na dostupny zbyvajici prostor
        oxygen_to_add = max(0.0, min(remaining, oxygen_fill_bar))

    # Zbytek doplnime vzduchem
    air_to_add = max(0.0, remaining - oxygen_to_add)
    return round(oxygen_to_add, 2), round(air_to_add, 2)
