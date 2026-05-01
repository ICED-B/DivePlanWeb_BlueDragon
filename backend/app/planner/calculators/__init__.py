from __future__ import annotations
# kazdy modul implementuje jeden vypocet (kalkulacky)
# exportuje pro zbytek aplikace

from .sac_rmv import weighted_ata_for_segments, sac_from_consumption, calc_rmv, calc_sac_bar_min
from .gas_reserves import gas_used_l_from_pressure_drop, gas_needed_for_profile

from .ndl_table import ndl_for_depth, ndl_table_for_depths, ndl_full_table, deco_stops_for_dive, resolve_mix_to_fo2

from .ppo2 import calc_ppo2
from .mod import calc_mod
from .best_mix import calc_best_mix
from .ead import calc_ead
from .end import calc_end

from .tank_gas_content import calc_tank_gas_content_liters
from .required_gas import calc_required_gas_liters
from .consumed_gas import calc_consumed_gas, ConsumedGasResult
from .dive_time import calc_dive_time_min, calc_dive_time_from_tank

from .otu import calc_otu
from .cns import calc_cns, CNSResult


__all__ = [
    # SAC / RMV
    "weighted_ata_for_segments",
    "sac_from_consumption",
    "calc_rmv",
    "calc_sac_bar_min",
    # Gas reserves (interni)
    "gas_used_l_from_pressure_drop",
    "gas_needed_for_profile",
    # NDL / Deco
    "ndl_for_depth",
    "ndl_table_for_depths",
    "ndl_full_table",
    "deco_stops_for_dive",
    "resolve_mix_to_fo2",
    # Single-value calcs
    "calc_ppo2",
    "calc_mod",
    "calc_best_mix",
    "calc_ead",
    "calc_end",
    # Gas / tank
    "calc_tank_gas_content_liters",
    "calc_required_gas_liters",
    "calc_consumed_gas",
    "ConsumedGasResult",
    "calc_dive_time_min",
    "calc_dive_time_from_tank",
    # Toxicita kysliku
    "calc_otu",
    "calc_cns",
    "CNSResult",
]
