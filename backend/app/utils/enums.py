# Enum pouzivane v modelech schematech a routach (odvozeny od str)
from enum import Enum


class UserRoleEnum(str, Enum):  # role uzivatelu odpovida AppUser.role
    ADMIN = "admin"
    USER = "user"

    @classmethod
    def list(cls) -> list[str]:  # vraci seznam vsech hodnot (pro validaci nebo swagger)
        return [e.value for e in cls]


class GasTypeEnum(str, Enum):   # dychaci smesi v modelu gas
    AIR = "air"
    NITROX = "nitrox"
    TRIMIX = "trimix"
    OXYGEN = "oxygen"
    HELIOX = "heliox"


class DiveEventTypeEnum(str, Enum): # typy udalosti behem ponoru (odpovida schema DiveEvent)
    DESCENT = "descent"
    ASCENT = "ascent"
    DECO_STOP = "deco_stop"
    SURFACE = "surface"
    WAYPOINT = "waypoint"
    OTHER = "other"


class TankUnitEnum(str, Enum):  # objem tlakove lahve
    LITERS = "l"
    CUBIC_FEET = "cuft"


class PressureUnitEnum(str, Enum):  # tlak plynu v lahvi
    BAR = "bar"
    PSI = "psi"


class DepthUnitEnum(str, Enum):     # hloubka
    METERS = "m"
    FEET = "ft"


class TemperatureUnitEnum(str, Enum):   # teplota
    CELSIUS = "°C"
    FAHRENHEIT = "°F"


class DurationUnitEnum(str, Enum):  # cas, doba trvani
    MINUTES = "min"
    SECONDS = "s"


class DistanceUnitEnum(str, Enum):  # vzdalenost
    METERS = "m"
    FEET = "ft"


class VolumeUnitEnum(str, Enum):    # objem plynu spotrebovany nebo dostupny
    LITERS = "l"
    CUBIC_FEET = "cuft"


class WeightUnitEnum(str, Enum):    # hmotnost zavazi vybaveni
    KILOGRAM = "kg"
    POUND = "lb"
