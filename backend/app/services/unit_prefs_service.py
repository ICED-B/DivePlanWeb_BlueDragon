
# uzivatelske preference jednotek, (samostatna tabulka UnitPrefs nebo JSON na AppUser)
# backend/app/services/unit_prefs_service.py
from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, Optional, Tuple

from sqlalchemy import select

from app.db import db
from app.utils.enums import (
    DepthUnitEnum,
    DistanceUnitEnum,
    PressureUnitEnum,
    TemperatureUnitEnum,
    VolumeUnitEnum,
    WeightUnitEnum,
    DurationUnitEnum,
)
from app.utils.units import (
    UnitPrefs,
    convert_depth,
    convert_pressure,
    convert_temperature,
    convert_volume,
    convert_distance,
    convert_weight,
    convert_duration,
)


class UnitPrefsServiceError(Exception):
    """Vyjimka preferenci, pri chybe ulozeni nebo nenalezeni uzivatele"""


def prefs_to_dict(p: UnitPrefs) -> Dict[str, str]:
    # Serializace UnitPrefs do dictu (hodnoty enumu prevedeny na string)
    d = asdict(p)
    return {k: (v.value if hasattr(v, "value") else v) for k, v in d.items()}


def prefs_from_dict(raw: Dict[str, Any]) -> UnitPrefs:
    # Deserializace UnitPrefs z dictu (chybejici se doplni vychozimi hodnotami)
    defaults = UnitPrefs()

    def pick(name: str, enum, default_value):
        # precte hodnotu z raw dictu a prevede ji na enum, pri chybe vrati default
        v = (raw or {}).get(name, None)
        try:
            if v is None:
                return default_value
            # Akceptujeme jak enum, tak string hodnotu
            return enum(v) if not isinstance(v, enum) else v
        except Exception:
            return default_value

    return UnitPrefs(
        depth=pick("depth", DepthUnitEnum, defaults.depth),
        distance=pick("distance", DistanceUnitEnum, defaults.distance),
        pressure=pick("pressure", PressureUnitEnum, defaults.pressure),
        temperature=pick("temperature", TemperatureUnitEnum, defaults.temperature),
        volume=pick("volume", VolumeUnitEnum, defaults.volume),
        weight=pick("weight", WeightUnitEnum, defaults.weight),
        duration=pick("duration", DurationUnitEnum, defaults.duration),
    )


# Ziskani/ulozeni preferenci
def _resolve_storage_model():
    # Uloziste uzivatelskych preferenci v model UnitPrefs v app.models.unit-prefs, Json sloupec na AppUser
    # Tabulka unit_prefs
    try:
        from app.models.unit_prefs import UnitPrefs as UnitPrefsModel  # type: ignore

        return "table", UnitPrefsModel
    except Exception:
        pass

    # JSON sloupec na AppUser
    try:
        from app.models.app_user import AppUser  # type: ignore

        # Hledame ocekavane JSON sloupce
        if hasattr(AppUser, "unit_prefs_json"):
            return "appuser_json", AppUser
        if hasattr(AppUser, "prefs"):
            return "appuser_json", AppUser
    except Exception:
        pass

    raise UnitPrefsServiceError(
        "Nebylo nalezeno uloziste pro jednotkove preference. "
        "Vytvor model app.models.unit_prefs.UnitPrefs (user_id, data JSON) "
        "nebo pridej JSON sloupec 'unit_prefs_json' na AppUser."
    )


def get_prefs_for_user(user_id: int) -> UnitPrefs:
    # Nacte preference jednotek uzivatele, pokud neexistuje vrati vychozi metricke UnitPrefs()
    mode, Model = _resolve_storage_model()

    if mode == "table":
        # Ocekava se: sloupce user_id (PK/FK) a data (JSON) nebo jednotlive string sloupce
        row = db.session.scalars(
            select(Model).where(getattr(Model, "user_id") == user_id)
        ).first()
        if not row:
            return UnitPrefs()

        # Preferuj JSON pole 'data' fallback na jednotlive sloupce
        raw: Dict[str, Any] = {}
        if hasattr(row, "data") and getattr(row, "data") is not None:
            raw = dict(getattr(row, "data"))
        else:
            # Precteme jednotlive sloupce, pokud JSON pole 'data' neexistuje
            for field in prefs_to_dict(UnitPrefs()).keys():
                if hasattr(row, field):
                    raw[field] = getattr(row, field)

        return prefs_from_dict(raw)

    # mode == "appuser_json" preference ulozeny jako JSON
    user = db.session.get(Model, user_id)
    if not user:
        return UnitPrefs()

    raw: Dict[str, Any] = {}
    if hasattr(user, "unit_prefs_json") and getattr(user, "unit_prefs_json") is not None:
        raw = dict(getattr(user, "unit_prefs_json"))
    elif hasattr(user, "prefs") and getattr(user, "prefs") is not None:
        prefs_blob = getattr(user, "prefs")
        if isinstance(prefs_blob, dict):
            raw = dict(prefs_blob.get("units") or {})

    return prefs_from_dict(raw)


def set_prefs_for_user(user_id: int, new_prefs: UnitPrefs) -> UnitPrefs:
    # Ulozi nebo aktualizuje preference jednotek uzivatele
    # automaticky vytvori novy zaznam (pripadne UnitprefsServiceError pri selhani commitu)
    mode, Model = _resolve_storage_model()
    data = prefs_to_dict(new_prefs)

    if mode == "table":
        row = db.session.scalars(
            select(Model).where(getattr(Model, "user_id") == user_id)
        ).first()
        if not row:
            # Zaznam neexistuje, vytvorime novy
            row = Model(user_id=user_id)  # type: ignore
            db.session.add(row)

        if hasattr(row, "data"):
            setattr(row, "data", data)
        else:
            # Ulozime jako jednotlive string sloupce
            for k, v in data.items():
                if hasattr(row, k):
                    setattr(row, k, v)

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise UnitPrefsServiceError("Ulozeni preferenci selhalo.")
        return new_prefs

    # mode == "appuser_json"
    user = db.session.get(Model, user_id)
    if not user:
        raise UnitPrefsServiceError("Uzivatel nenalezen.")

    if hasattr(user, "unit_prefs_json"):
        # JSON sloupec na AppUser
        setattr(user, "unit_prefs_json", data)
    else:
        # JSON prefs zachovame ostatni klice, zmenime jen units
        current = getattr(user, "prefs", None)
        if not isinstance(current, dict):
            current = {}
        current["units"] = data
        setattr(user, "prefs", current)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise UnitPrefsServiceError("Ulozeni preferenci selhalo.")

    return new_prefs


def normalize_values(
    *,
    depth: Optional[Tuple[float, DepthUnitEnum]] = None,
    pressure: Optional[Tuple[float, PressureUnitEnum]] = None,
    temperature: Optional[Tuple[float, TemperatureUnitEnum]] = None,
    volume: Optional[Tuple[float, VolumeUnitEnum]] = None,
    distance: Optional[Tuple[float, DistanceUnitEnum]] = None,
    weight: Optional[Tuple[float, WeightUnitEnum]] = None,
    duration: Optional[Tuple[float, DurationUnitEnum]] = None,
    prefs: Optional[UnitPrefs] = None,
) -> Dict[str, tuple[float, str]]:

    # jednotlive hodnoty prevadi do uzivatelskych preferenci
    # Pouzijeme predane preference, nebo vychozi metricky UnitPrefs
    p = prefs or UnitPrefs()
    out: Dict[str, tuple[float, str]] = {}

    if depth is not None:
        v, u = depth
        vv = convert_depth(v, u, p.depth)
        out["depth"] = (vv, p.depth.value)

    if pressure is not None:
        v, u = pressure
        vv = convert_pressure(v, u, p.pressure)
        out["pressure"] = (vv, p.pressure.value)

    if temperature is not None:
        v, u = temperature
        vv = convert_temperature(v, u, p.temperature)
        out["temperature"] = (vv, p.temperature.value)

    if volume is not None:
        v, u = volume
        vv = convert_volume(v, u, p.volume)
        out["volume"] = (vv, p.volume.value)

    if distance is not None:
        v, u = distance
        vv = convert_distance(v, u, p.distance)
        out["distance"] = (vv, p.distance.value)

    if weight is not None:
        v, u = weight
        vv = convert_weight(v, u, p.weight)
        out["weight"] = (vv, p.weight.value)

    if duration is not None:
        v, u = duration
        vv = convert_duration(v, u, p.duration)
        out["duration"] = (vv, p.duration.value)

    return out
