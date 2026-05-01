from __future__ import annotations
# Central Nervous System CNS, metodou NOAA ceiling
# ppO2 = FO2 * ATA(depth)
# MBT = NOAA table pro ppO2
# CNS% = (bottom_time / MBT) * 100

from dataclasses import dataclass
from app.utils.enums import DepthUnitEnum
from app.services.gas_service import ata_at_depth
from app.planner.calculators.validators import fraction01, non_negative, positive


# NOAA single-exposure limits (minuty) table
# Klic = ppO2 [ATA], hodnota = MBT (Maximum Bottom Time) [min]
_NOAA_MBT: dict[float, float] = {
    0.6: 720.0,
    0.7: 570.0,
    0.8: 450.0,
    0.9: 360.0,
    1.0: 300.0,
    1.1: 240.0,
    1.2: 210.0,
    1.3: 180.0,
    1.4: 150.0,
    1.5: 120.0,
    1.6:  45.0,
}

_NOAA_KEYS = sorted(_NOAA_MBT.keys())   # [0.6, 0.7, ..., 1.6]
_PP_MIN = _NOAA_KEYS[0]   # 0.6 ATA spodni prah CNS toxicity
_PP_MAX = _NOAA_KEYS[-1]  # 1.6 ATA horni limit tabulky


def _ceiling_mbt(pp: float) -> float:
    # Vrati MBT pro dane ppO2 (nejblizsi vyssi hodnota v tabulce)
    # Pokud ppO2 < 0.6: vraci bez zateze CNS | Pokud ppO2 > 1.6: vraci nejprisnejsi limit
    if pp < _PP_MIN:        # pod prahem zadna CNS toxicita
        return 0.0
    for k in _NOAA_KEYS:
        if pp <= k:            # prvni klic >= pp = ceiling
            return _NOAA_MBT[k]
    return _NOAA_MBT[_PP_MAX]    # pp > 1.6 pouzijeme nejprisnejsi limit


@dataclass(frozen=True)
class CNSResult:    # vysledek CNS vypoctu
    pp_o2_ata: float     # Vypoctene ppO2 = FO2 * ATA
    mbt_min: float       # Maximum Bottom Time z NOAA tabulky (ceiling)
    cns_percent: float   # (BT / MBT) * 100
    warning: str         # Varovani pri prekroceni limitu


def calc_cns(
    *,
    f_o2: float,
    depth: float,
    time_min: float,
    depth_unit: DepthUnitEnum = DepthUnitEnum.METERS,
) -> CNSResult:
    # vypocita CNS% pro zadany plyn, hloubku a cas
    # (ppO2 = FO2 * ATA(depth)), (MBT = NOAA table pro ppO2), (CNS% = (bottom_time / MBT) * 100)

    f = fraction01(f_o2, "f_o2", min_value=0.0)
    d = non_negative(depth, "depth")
    t = positive(time_min, "time_min")


    ata = float(ata_at_depth(d, depth_unit))        # Absolutni tlak v ATA pro danou hloubku
    pp = round(f * ata, 3)     # ppO2 zaokrouhleno na 3 mista (konzistentni s NOAA)

    mbt = _ceiling_mbt(pp)

    warning = ""
    if pp > _PP_MAX:        # Nad maximem tabulky -- extremni riziko
        warning = (
            f"ppO2 = {pp} ATA prekracuje maximalni limit {_PP_MAX} ATA! "
            "Extremne vysoke riziko konvulzi."
        )
    elif mbt <= 0.0:        # Pod prahem CNS neni relevantni
        return CNSResult(
            pp_o2_ata=pp,
            mbt_min=0.0,
            cns_percent=0.0,
            warning="ppO2 pod 0.6 ATA -- CNS toxicita neni relevantni.",
        )

    # CNS% = cas / MBT * 100
    cns = (t / mbt) * 100.0

    if not warning and cns > 80.0:      # Doporuceny denni limit je 80 %
        warning = (
            f"CNS {round(cns, 1)} % prekracuje doporuceny limit 80 %. "
            "Po ponoru je nutna pauza."
        )

    return CNSResult(
        pp_o2_ata=pp,
        mbt_min=round(mbt, 1),
        cns_percent=round(cns, 1),
        warning=warning,
    )
