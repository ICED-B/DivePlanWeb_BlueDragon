# statistiky pro uzivatele i vsechny

from __future__ import annotations

from typing import Any, Dict, List, Optional
from sqlalchemy import func, select, desc, and_

from app.db import db
from app.models.dive import Dive
from app.models.dive_tank import DiveTank
from app.models.gas_mix import GasMix
from app.models.tank import Tank
from app.models.dive_event import DiveEvent
from app.models.tag import Tag
from app.models.dive_tag import DiveTag
from app.models.site import Site
from app.models.license import License


class ExtendedStatsServiceError(Exception):
    """Vyjimka rozsirenych statistik pro budouci pouziti pri chybach dotazu."""


def _to_float(v) -> Optional[float]:    # prevod na float, none pri nepreveditelne
    try:
        return None if v is None else float(v)
    except Exception:
        return None


# UZIVATELSKE STATISTIKY (Top 5)

def get_user_gas_mix_stats(user_id: int, limit: int = 5) -> List[Dict[str, Any]]:
    # vraci Top-N pouzivanych plynnovych smesi, odvozuje se z poctu zaznamu spojenych s ponory
    q = (
        select(
            GasMix.gas_mix_id,
            GasMix.name,
            GasMix.gas_type,
            GasMix.o2_percent,
            GasMix.he_percent,
            func.count(DiveTank.dive_tank_id).label("uses"),
        )
        .select_from(DiveTank)
        .join(Dive, Dive.dive_id == DiveTank.dive_id)
        .join(GasMix, GasMix.gas_mix_id == DiveTank.gas_mix_id)
        .where(and_(Dive.user_id == user_id))
        .group_by(GasMix.gas_mix_id, GasMix.name, GasMix.gas_type, GasMix.o2_percent, GasMix.he_percent)
        .order_by(desc(func.count(DiveTank.dive_tank_id)))
        .limit(limit)
    )
    rows = db.session.execute(q).all()
    return [
        {
            "gas_mix_id": r[0],
            "name": r[1],
            "gas_type": r[2],
            "o2_percent": _to_float(r[3]),
            "he_percent": _to_float(r[4]),
            "uses": int(r[5]),
        }
        for r in rows
    ]


def get_user_tank_stats(user_id: int, limit: int = 5) -> List[Dict[str, Any]]:
    # vraci Top-N pouzitych lahvi ze zaznamu DiveTank se spolecnym tank_id
    q = (
        select(
            Tank.tank_id,
            Tank.volume_l,
            Tank.work_pressure_bar,
            Tank.material,
            func.count(DiveTank.dive_tank_id).label("uses"),
        )
        .select_from(DiveTank)
        .join(Dive, Dive.dive_id == DiveTank.dive_id)
        .join(Tank, Tank.tank_id == DiveTank.tank_id)
        .where(and_(Dive.user_id == user_id))
        .group_by(Tank.tank_id, Tank.volume_l, Tank.work_pressure_bar, Tank.material)
        .order_by(desc(func.count(DiveTank.dive_tank_id)))
        .limit(limit)
    )
    rows = db.session.execute(q).all()
    return [
        {
            "tank_id": r[0],
            "volume_l": _to_float(r[1]),
            "work_pressure_bar": _to_float(r[2]),
            "material": r[3],
            "uses": int(r[4]),
        }
        for r in rows
    ]


def get_user_tag_stats(user_id: int, limit: int = 5) -> List[Dict[str, Any]]:
    # vraci nejcasteji pouzite tagy
    q = (
        select(
            Tag.tag_id,
            Tag.name,
            func.count(DiveTag.dive_id).label("uses"),
        )
        .select_from(DiveTag)
        .join(Dive, Dive.dive_id == DiveTag.dive_id)
        .join(Tag, Tag.tag_id == DiveTag.tag_id)
        .where(and_(Dive.user_id == user_id))
        .group_by(Tag.tag_id, Tag.name)
        .order_by(desc(func.count(DiveTag.dive_id)))
        .limit(limit)
    )
    rows = db.session.execute(q).all()
    return [{"tag_id": r[0], "name": r[1], "uses": int(r[2])} for r in rows]


def get_user_dive_event_stats(user_id: int, limit: int = 5) -> List[Dict[str, Any]]:
    # vraci nejcastejsi udalosti
    q = (
        select(
            DiveEvent.type,
            func.count(DiveEvent.event_id).label("uses"),
        )
        .select_from(DiveEvent)
        .join(Dive, Dive.dive_id == DiveEvent.dive_id)
        .where(and_(Dive.user_id == user_id))
        .group_by(DiveEvent.type)
        .order_by(desc(func.count(DiveEvent.event_id)))
        .limit(limit)
    )
    rows = db.session.execute(q).all()
    return [{"type": r[0], "uses": int(r[1])} for r in rows]


def get_user_circuit_stats(user_id: int, limit: int = 5) -> List[Dict[str, Any]]:
    # Vraci pouziti dychacich systemu
    q = (
        select(
            Dive.breathing_system,
            func.count(Dive.dive_id).label("dives"),
        )
        .where(Dive.user_id == user_id)
        .group_by(Dive.breathing_system)
        .order_by(desc(func.count(Dive.dive_id)))
        .limit(limit)
    )
    rows = db.session.execute(q).all()
    return [{"breathing_system": r[0], "dives": int(r[1])} for r in rows]


def get_user_license_stats(user_id: int, limit: int = 5) -> List[Dict[str, Any]]:
    # Vraci licence pouzitych u ponoru, ponory bez licence jsou vyrazeny
    q = (
        select(
            License.license_id,
            License.agency,
            License.certification,
            func.count(Dive.dive_id).label("dives"),
        )
        .select_from(Dive)
        .join(License, License.license_id == Dive.license_id)
        .where(and_(Dive.user_id == user_id))
        .group_by(License.license_id, License.agency, License.certification)
        .order_by(desc(func.count(Dive.dive_id)))
        .limit(limit)
    )
    rows = db.session.execute(q).all()
    return [
        {"license_id": r[0], "agency": r[1],
            "certification": r[2], "dives": int(r[3])}
        for r in rows
    ]


def get_user_site_country_stats(user_id: int, limit: int = 5) -> List[Dict[str, Any]]:
    # Vraci zeme spojene s ponory Top-N
    q = (
        select(
            Site.country,
            func.count(Dive.dive_id).label("dives"),
        )
        .select_from(Dive)
        .join(Site, Site.site_id == Dive.site_id)
        .where(and_(Dive.user_id == user_id, Site.country.isnot(None)))
        .group_by(Site.country)
        .order_by(desc(func.count(Dive.dive_id)))
        .limit(limit)
    )
    rows = db.session.execute(q).all()
    return [{"country": r[0], "dives": int(r[1])} for r in rows]


def get_user_site_region_stats(user_id: int, limit: int = 5) -> List[Dict[str, Any]]:
    # vraci top-N regiony
    q = (
        select(
            Site.region,
            func.count(Dive.dive_id).label("dives"),
        )
        .select_from(Dive)
        .join(Site, Site.site_id == Dive.site_id)
        .where(and_(Dive.user_id == user_id, Site.region.isnot(None)))
        .group_by(Site.region)
        .order_by(desc(func.count(Dive.dive_id)))
        .limit(limit)
    )
    rows = db.session.execute(q).all()
    return [{"region": r[0], "dives": int(r[1])} for r in rows]



# GLOBALNI STATISTIKY (Top 10) pro vsechny uzivatele

def get_global_gas_mix_stats(limit: int = 10) -> List[Dict[str, Any]]:
    # vraci nejvice pouzivane plynnove smesi
    q = (
        select(
            GasMix.gas_mix_id,
            GasMix.name,
            GasMix.gas_type,
            GasMix.o2_percent,
            GasMix.he_percent,
            func.count(DiveTank.dive_tank_id).label("uses"),
        )
        .select_from(DiveTank)
        .join(GasMix, GasMix.gas_mix_id == DiveTank.gas_mix_id)
        .group_by(GasMix.gas_mix_id, GasMix.name, GasMix.gas_type, GasMix.o2_percent, GasMix.he_percent)
        .order_by(desc(func.count(DiveTank.dive_tank_id)))
        .limit(limit)
    )
    rows = db.session.execute(q).all()
    return [
        {
            "gas_mix_id": r[0],
            "name": r[1],
            "gas_type": r[2],
            "o2_percent": _to_float(r[3]),
            "he_percent": _to_float(r[4]),
            "uses": int(r[5]),
        }
        for r in rows
    ]


def get_global_tank_stats(limit: int = 10) -> List[Dict[str, Any]]:
    # nejvice pouzivane lahve
    q = (
        select(
            Tank.tank_id,
            Tank.volume_l,
            Tank.work_pressure_bar,
            Tank.material,
            func.count(DiveTank.dive_tank_id).label("uses"),
        )
        .select_from(DiveTank)
        .join(Tank, Tank.tank_id == DiveTank.tank_id)
        .group_by(Tank.tank_id, Tank.volume_l, Tank.work_pressure_bar, Tank.material)
        .order_by(desc(func.count(DiveTank.dive_tank_id)))
        .limit(limit)
    )
    rows = db.session.execute(q).all()
    return [
        {
            "tank_id": r[0],
            "volume_l": _to_float(r[1]),
            "work_pressure_bar": _to_float(r[2]),
            "material": r[3],
            "uses": int(r[4]),
        }
        for r in rows
    ]


def get_global_tag_stats(limit: int = 10) -> List[Dict[str, Any]]:
    # nejcastejsi tagy
    q = (
        select(
            Tag.name,
            func.count(DiveTag.dive_id).label("uses"),
        )
        .select_from(DiveTag)
        .join(Tag, Tag.tag_id == DiveTag.tag_id)
        .group_by(Tag.name)
        .order_by(desc(func.count(DiveTag.dive_id)))
        .limit(limit)
    )
    rows = db.session.execute(q).all()
    return [{"name": r[0], "uses": int(r[1])} for r in rows]


def get_global_dive_event_stats(limit: int = 10) -> List[Dict[str, Any]]:
    # nejcastejsi typy udalosti
    q = (
        select(
            DiveEvent.type,
            func.count(DiveEvent.event_id).label("uses"),
        )
        .group_by(DiveEvent.type)
        .order_by(desc(func.count(DiveEvent.event_id)))
        .limit(limit)
    )
    rows = db.session.execute(q).all()
    return [{"type": r[0], "uses": int(r[1])} for r in rows]


def get_global_circuit_stats(limit: int = 10) -> List[Dict[str, Any]]:
    # nejcastejsi dychaci systemy
    q = (
        select(
            Dive.breathing_system,
            func.count(Dive.dive_id).label("dives"),
        )
        .group_by(Dive.breathing_system)
        .order_by(desc(func.count(Dive.dive_id)))
        .limit(limit)
    )
    rows = db.session.execute(q).all()
    return [{"breathing_system": r[0], "dives": int(r[1])} for r in rows]


def get_global_license_stats(limit: int = 10) -> List[Dict[str, Any]]:
    # nejcastejsi pouzite certifikace
    q = (
        select(
            License.agency,
            License.certification,
            func.count(Dive.dive_id).label("dives"),
        )
        .select_from(Dive)
        .join(License, License.license_id == Dive.license_id)
        .group_by(License.agency, License.certification)
        .order_by(desc(func.count(Dive.dive_id)))
        .limit(limit)
    )
    rows = db.session.execute(q).all()
    return [{"agency": r[0], "certification": r[1], "dives": int(r[2])} for r in rows]


def get_global_site_country_stats(limit: int = 10) -> List[Dict[str, Any]]:
    # zeme s nejvetsim poctem ponoru
    q = (
        select(
            Site.country,
            func.count(Dive.dive_id).label("dives"),
        )
        .select_from(Dive)
        .join(Site, Site.site_id == Dive.site_id)
        .where(Site.country.isnot(None))
        .group_by(Site.country)
        .order_by(desc(func.count(Dive.dive_id)))
        .limit(limit)
    )
    rows = db.session.execute(q).all()
    return [{"country": r[0], "dives": int(r[1])} for r in rows]


def get_global_site_region_stats(limit: int = 10) -> List[Dict[str, Any]]:
    # regiony s nejvetsim poctem ponoru
    q = (
        select(
            Site.region,
            func.count(Dive.dive_id).label("dives"),
        )
        .select_from(Dive)
        .join(Site, Site.site_id == Dive.site_id)
        .where(Site.region.isnot(None))
        .group_by(Site.region)
        .order_by(desc(func.count(Dive.dive_id)))
        .limit(limit)
    )
    rows = db.session.execute(q).all()
    return [{"region": r[0], "dives": int(r[1])} for r in rows]
