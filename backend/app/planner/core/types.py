# backend/app/planner/core/types.py
from __future__ import annotations

# Definuej aliasy, vyjimku PlannerSeviceError a datove struktury Segment a TankSpec
from dataclasses import dataclass
from typing import Iterable, Union
from app.utils.enums import DepthUnitEnum

# Numericky typ pouzivany pro hodnoty, ktere mohou byt int nebo float
Number = Union[float, int]


class PlannerServiceError(Exception):
    """Vyjimka planovace pro chyby aplikacni logiky."""
    pass


@dataclass
class Segment:    # Jedne segment profilu pro spotrebu (avg_depth, duration_min)
    duration_min: Number
    avg_depth: Number
    depth_unit: DepthUnitEnum = DepthUnitEnum.METERS


@dataclass
class TankSpec: # param lahve pro vypocet mnozstvi plynu
    volume_l: Number
    working_pressure_bar: Number
