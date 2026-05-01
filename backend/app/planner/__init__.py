from __future__ import annotations

# exportuje zakladni datove typy a funkce pro NDL/deko planovani
# vnitrni moduly nejsou nutne importovat primo
from .core.types import (
    Segment,
    TankSpec,
    PlannerServiceError,
    Number,
)
from .core.deco_tables import (
    plan_dive,
    get_deco_plan_from_tables,
)
