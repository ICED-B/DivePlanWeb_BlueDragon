from __future__ import annotations
# OTU (Oxygen Toxicity Units) kyslikova toxicita
# OTU = ((ppO2 - 0.5) / 0.5)^(-5/6) * cas

import math

def calc_otu(*, pp_o2_ata: float, time_min: float) -> float:
    # vypocita OTU pro jedne segment kdy [rate = ((ppO2 - 0.5) / 0.5) ^ (-5/6)], [OTU  = rate * time_min]
    if pp_o2_ata <= 0:
        raise ValueError("pp_o2_ata musi byt > 0.")
    if time_min <= 0:
        raise ValueError("time_min musi byt > 0.")

    if pp_o2_ata <= 0.5:        # Pod 0.5 ATA se OTU standardne nepocita
        return 0.0

    rate = math.pow((pp_o2_ata - 0.5) / 0.5, -5.0 / 6.0)    # NOAA aproximace rychlosti OTU expozice
    otu = rate * time_min
    return round(float(otu), 1)
