# funkce pro prevody a normalize_* jednotek uzivatele (preferenci)
from __future__ import annotations

from dataclasses import dataclass
from typing import Union
from enum import Enum

from .enums import (
    DepthUnitEnum,
    DistanceUnitEnum,
    PressureUnitEnum,
    TemperatureUnitEnum,
    VolumeUnitEnum,
    WeightUnitEnum,
    DurationUnitEnum,
)

Number = Union[int, float]

# Prevodni konstanty
_M_TO_FT = 3.280839895013123
_BAR_TO_PSI = 14.503773773
_CUFT_TO_L = 28.316846592
_KG_TO_LB = 2.20462262185


# Prevodni funkce

def m_to_ft(value: Number) -> float:
    return float(value) * _M_TO_FT


def ft_to_m(value: Number) -> float:
    return float(value) / _M_TO_FT


def bar_to_psi(value: Number) -> float:
    return float(value) * _BAR_TO_PSI


def psi_to_bar(value: Number) -> float:
    return float(value) / _BAR_TO_PSI


def c_to_f(value: Number) -> float:
    return float(value) * 9.0 / 5.0 + 32.0


def f_to_c(value: Number) -> float:
    return (float(value) - 32.0) * 5.0 / 9.0


def l_to_cuft(value: Number) -> float:
    return float(value) / _CUFT_TO_L


def cuft_to_l(value: Number) -> float:
    return float(value) * _CUFT_TO_L


def kg_to_lb(value: Number) -> float:
    return float(value) * _KG_TO_LB


def lb_to_kg(value: Number) -> float:
    return float(value) / _KG_TO_LB


def min_to_sec(value: Number) -> float:
    return float(value) * 60.0


def sec_to_min(value: Number) -> float:
    return float(value) / 60.0


# Prevody dle enumu jednotek

def convert_depth(value: Number, from_u: DepthUnitEnum, to_u: DepthUnitEnum) -> float:
    if from_u == to_u:          # hloubka mezi m a ft
        return float(value)
    return m_to_ft(value) if (from_u == DepthUnitEnum.METERS and to_u == DepthUnitEnum.FEET) else ft_to_m(value)


def convert_distance(value: Number, from_u: DistanceUnitEnum, to_u: DistanceUnitEnum) -> float: 
    if from_u == to_u:                  # vzdalenost mezi m a ft
        return float(value)
    return m_to_ft(value) if (from_u == DistanceUnitEnum.METERS and to_u == DistanceUnitEnum.FEET) else ft_to_m(value)


def convert_pressure(value: Number, from_u: PressureUnitEnum, to_u: PressureUnitEnum) -> float:
    if from_u == to_u:              # prevod talku mezi bar psi
        return float(value)
    return bar_to_psi(value) if (from_u == PressureUnitEnum.BAR and to_u == PressureUnitEnum.PSI) else psi_to_bar(value)


def convert_temperature(value: Number, from_u: TemperatureUnitEnum, to_u: TemperatureUnitEnum) -> float:
    if from_u == to_u:              # prevod teploty mezi Celsius a Fahrenheit
        return float(value)
    return c_to_f(value) if (from_u == TemperatureUnitEnum.CELSIUS and to_u == TemperatureUnitEnum.FAHRENHEIT) else f_to_c(value)


def convert_volume(value: Number, from_u: VolumeUnitEnum, to_u: VolumeUnitEnum) -> float:
    if from_u == to_u:          # prevod objemu plynu mezi l a cuft
        return float(value)
    return l_to_cuft(value) if (from_u == VolumeUnitEnum.LITERS and to_u == VolumeUnitEnum.CUBIC_FEET) else cuft_to_l(value)


def convert_weight(value: Number, from_u: WeightUnitEnum, to_u: WeightUnitEnum) -> float:
    if from_u == to_u:          # prevod hmotnosti kg lb
        return float(value)
    return kg_to_lb(value) if (from_u == WeightUnitEnum.KILOGRAM and to_u == WeightUnitEnum.POUND) else lb_to_kg(value)


def convert_duration(value: Number, from_u: DurationUnitEnum, to_u: DurationUnitEnum) -> float:
    if from_u == to_u:                  # prevod casu min a sec
        return float(value)
    return min_to_sec(value) if (from_u == DurationUnitEnum.MINUTES and to_u == DurationUnitEnum.SECONDS) else sec_to_min(value)


# Uzivatelske preference jednotek

@dataclass(frozen=True)
class UnitPrefs:
    # Vychozi je metricka (pouziva se u normalize_ a planneru)
    depth: DepthUnitEnum = DepthUnitEnum.METERS
    distance: DistanceUnitEnum = DistanceUnitEnum.METERS
    pressure: PressureUnitEnum = PressureUnitEnum.BAR
    temperature: TemperatureUnitEnum = TemperatureUnitEnum.CELSIUS
    volume: VolumeUnitEnum = VolumeUnitEnum.LITERS
    weight: WeightUnitEnum = WeightUnitEnum.KILOGRAM
    duration: DurationUnitEnum = DurationUnitEnum.MINUTES


# pro formatovani

def format_value(value: Number, unit: Union[str, Enum], decimals: int = 2, with_unit: bool = True) -> str:
    # zaokrouhluje na dana desetinna mista, pokud with_unit=True prida symbol jednotky
    if isinstance(unit, Enum):
        unit = unit.value  # type: ignore[assignment]
    txt = f"{float(value):.{decimals}f}"
    return f"{txt} {unit}" if with_unit and unit else txt


# Normalizace preferenci uzivatele (hodnoty, jednotka)

def normalize_depth(value: Number, from_u: DepthUnitEnum, prefs: UnitPrefs) -> tuple[float, DepthUnitEnum]:
    v = convert_depth(value, from_u, prefs.depth)       # pref zvolena jednotka hloubky
    return v, prefs.depth


def normalize_pressure(value: Number, from_u: PressureUnitEnum, prefs: UnitPrefs) -> tuple[float, PressureUnitEnum]:
    v = convert_pressure(value, from_u, prefs.pressure) # pref zvolena jednotka talku
    return v, prefs.pressure


def normalize_temperature(value: Number, from_u: TemperatureUnitEnum, prefs: UnitPrefs) -> tuple[float, TemperatureUnitEnum]:
    v = convert_temperature(value, from_u, prefs.temperature)   # pref zvolena jednotka teploty
    return v, prefs.temperature


def normalize_volume(value: Number, from_u: VolumeUnitEnum, prefs: UnitPrefs) -> tuple[float, VolumeUnitEnum]:
    v = convert_volume(value, from_u, prefs.volume)     # pref zvolena jednotka objemu
    return v, prefs.volume


def normalize_distance(value: Number, from_u: DistanceUnitEnum, prefs: UnitPrefs) -> tuple[float, DistanceUnitEnum]:
    v = convert_distance(value, from_u, prefs.distance)     # pref zvolena jednotka vzdalenost
    return v, prefs.distance


def normalize_weight(value: Number, from_u: WeightUnitEnum, prefs: UnitPrefs) -> tuple[float, WeightUnitEnum]:
    v = convert_weight(value, from_u, prefs.weight) # pref zvolena jednotka hmotonosti
    return v, prefs.weight


def normalize_duration(value: Number, from_u: DurationUnitEnum, prefs: UnitPrefs) -> tuple[float, DurationUnitEnum]:
    v = convert_duration(value, from_u, prefs.duration)     # pref zvolena jednotka casu
    return v, prefs.duration
