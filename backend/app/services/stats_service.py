# statisticky pro uzivatele i globalni prehledy
# fallbacky nazvu sloupcu pro kompatibilitu s ruznym pojmenovanim
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional

from sqlalchemy import func, select, desc, and_

from app.db import db
import app.models as dive_models  # ocekava modul s tridami Dive, Site apod.


class StatsServiceError(Exception):
    """Vyjimka statisticke sluzby, vyhazovana pri nenalezeni modelu nebo chybejicich sloupcich."""


# Pomocne mapovani sloupcu (pro kompatibilitu mezi ruznymi variantami modelu)

def _col(model, *names: str): # vrati prvni existujici atribut dle zadanych nazvu nebo StatsServiceError
    for n in names:
        if hasattr(model, n):
            return getattr(model, n)
    raise StatsServiceError(
        f"Model {model} nema zadny z pozadovanych sloupcu: {', '.join(names)}")


def _maybe_col(model, *names: str): # vrati existujici atribut nebo None
    for n in names:
        if hasattr(model, n):
            return getattr(model, n)
    return None


def _to_float(v) -> Optional[float]:    # prevod na float, None pri chybe nebo None vstupu
    try:
        return None if v is None else float(v)
    except Exception:
        return None


def _safe_str(v) -> Optional[str]:  # prevod na string, None pri chybe nebo None vstupu
    if v is None:
        return None
    try:
        return str(v)
    except Exception:
        return None


@dataclass
class BasicStats:   # statistiky sady ponoru
    dives_count: int
    total_duration_min: float
    avg_duration_min: float
    max_depth_m: float
    avg_depth_m: float
    avg_temp_c: Optional[float]


@dataclass
class TopSite:  # zebricek nejcastejsich lokalit
    site_name: str
    dives: int


@dataclass
class RecentDive:   # zebricek poslednich ponoru
    id: int
    start_time: Optional[str]
    duration_min: Optional[float]
    max_depth_m: Optional[float]
    site: Optional[str]


@dataclass
class DeepDive: # zebricek nejhlubsich ponoru
    id: int
    start_time: Optional[str]
    max_depth_m: Optional[float]
    duration_min: Optional[float]
    site: Optional[str]
    # Global muze ukazat i "kdo", pokud relationship existuje
    diver_name: Optional[str] = None


def get_user_stats(
    user_id: int,
    limit_recent: int = 5,
    top_deep_limit: int = 5,
    from_dt: Optional[Any] = None,
    to_dt: Optional[Any] = None,
) -> Dict[str, Any]:
    # vraci pozbirane statistiky pro uzivatele

    Dive = getattr(dive_models, "Dive", None)
    if Dive is None:
        raise StatsServiceError("Model Dive nebyl nalezen.")

    # Sloupce, ktere budeme pouzivat (bezpecne s fallbacky nazvu)
    c_id = _col(Dive, "id", "dive_id")
    c_user = _maybe_col(Dive, "diver_id", "user_id", "app_user_id", "owner_id")
    c_start = _maybe_col(Dive, "start_time", "started_at")
    c_duration = _maybe_col(Dive, "duration_min", "duration")
    c_max_depth = _maybe_col(Dive, "max_depth_m", "max_depth")
    c_avg_depth = _maybe_col(Dive, "avg_depth_m", "avg_depth")
    c_temp = _maybe_col(Dive, "temperature_c", "water_temp_c")
    c_site_rel = _maybe_col(Dive, "site")

    if c_user is None:
        raise StatsServiceError(
            "Dive nema sloupec diver_id (ani user_id/app_user_id/owner_id).")
    if c_max_depth is None:
        raise StatsServiceError(
            "Dive nema sloupec max_depth_m (ani max_depth).")

    # Zakladni filtrovaci podminka, vzdy filtrujeme dle uzivatele
    conds = [c_user == user_id]
    # Volitelne casove omezeni (pokud je k dispozici sloupec start_time)
    if from_dt is not None and c_start is not None:
        conds.append(c_start >= from_dt)
    if to_dt is not None and c_start is not None:
        conds.append(c_start < to_dt)

    # Agregacni dotaz: pocty, soucty a prumery v jednom SQL volani
    q_basic = select(
        func.count(c_id),
        func.coalesce(func.sum(c_duration), 0),
        func.coalesce(func.avg(c_duration), 0.0),
        func.coalesce(func.max(c_max_depth), 0.0),
        func.coalesce(func.avg(c_avg_depth), 0.0),
        func.avg(c_temp) if c_temp is not None else None,
    ).where(and_(*conds))

    res = db.session.execute(q_basic).first()
    dives_count = int(res[0]) if res and res[0] is not None else 0
    total_duration = float(res[1]) if res and res[1] is not None else 0.0
    avg_duration = float(res[2]) if res and res[2] is not None else 0.0
    max_depth = float(res[3]) if res and res[3] is not None else 0.0
    avg_depth = float(res[4]) if res and res[4] is not None else 0.0
    avg_temp = float(res[5]) if res and len(
        res) > 5 and res[5] is not None else None

    basic = BasicStats(
        dives_count=dives_count,
        total_duration_min=total_duration,
        avg_duration_min=avg_duration,
        max_depth_m=max_depth,
        avg_depth_m=avg_depth,
        avg_temp_c=avg_temp,
    )

    # Top lokality (pokud existuje relationship site->name na modelu Dive)
    top_sites: List[TopSite] = []
    Site = getattr(dive_models, "Site", None)

    if c_site_rel is not None and Site is not None and hasattr(Site, "name"):
        q_sites = (
            select(dive_models.Site.name, func.count(c_id))
            .select_from(Dive)
            .join(getattr(Dive, "site"))
            .where(and_(*conds))
            .group_by(dive_models.Site.name)
            .order_by(desc(func.count(c_id)))
            .limit(5)
        )
        for name, cnt in db.session.execute(q_sites).all():
            top_sites.append(TopSite(site_name=name, dives=int(cnt)))

    # Posledni ponory serazene dle casu (nebo ID jako fallback)
    recent: List[RecentDive] = []
    q_recent = (
        select(Dive)
        .where(and_(*conds))
        .order_by(desc(c_start if c_start is not None else c_id))
        .limit(limit_recent)
    )
    for d in db.session.scalars(q_recent).all():
        site_name = None
        try:
            site_obj = getattr(d, "site", None)
            site_name = getattr(
                site_obj, "name", None) if site_obj is not None else None
        except Exception:
            site_name = None

        # Pouzijeme dive_id nebo id jako fallback primarniho klice
        dive_pk = getattr(d, "id", None) or getattr(d, "dive_id", None)

        recent.append(
            RecentDive(
                id=int(dive_pk),
                start_time=_safe_str(
                    getattr(d, "start_time", None) or getattr(d, "started_at", None)),
                duration_min=_to_float(
                    getattr(d, "duration_min", None) or getattr(d, "duration", None)),
                max_depth_m=_to_float(
                    getattr(d, "max_depth_m", None) or getattr(d, "max_depth", None)),
                site=site_name,
            )
        )

    # Top nejhlubbsi ponory uzivatele, serazene dle max hloubky
    top_deep: List[DeepDive] = []
    q_deep = (
        select(Dive)
        .where(and_(*conds))
        .order_by(desc(c_max_depth), desc(c_start if c_start is not None else c_id))
        .limit(top_deep_limit)
    )
    for d in db.session.scalars(q_deep).all():
        site_name = None
        try:
            site_obj = getattr(d, "site", None)
            site_name = getattr(
                site_obj, "name", None) if site_obj is not None else None
        except Exception:
            site_name = None

        dive_pk = getattr(d, "id", None) or getattr(d, "dive_id", None)

        top_deep.append(
            DeepDive(
                id=int(dive_pk),
                start_time=_safe_str(
                    getattr(d, "start_time", None) or getattr(d, "started_at", None)),
                max_depth_m=_to_float(
                    getattr(d, "max_depth_m", None) or getattr(d, "max_depth", None)),
                duration_min=_to_float(
                    getattr(d, "duration_min", None) or getattr(d, "duration", None)),
                site=site_name,
                diver_name=None,  # u user_stats jmeno potapece nepotrebujeme
            )
        )

    return {
        "basic": asdict(basic),
        "top_sites": [asdict(x) for x in top_sites],
        "recent_dives": [asdict(x) for x in recent],
        "top_deep_dives": [asdict(x) for x in top_deep],
    }


def get_global_stats(limit_top_sites: int = 5, top_deep_limit: int = 10) -> Dict[str, Any]:
    # globalni statistiky vsech uzivatelu dohromady
    Dive = getattr(dive_models, "Dive", None)
    if Dive is None:
        raise StatsServiceError("Model Dive nebyl nalezen.")

    c_id = _col(Dive, "id", "dive_id")
    c_start = _maybe_col(Dive, "start_time", "started_at")
    c_duration = _maybe_col(Dive, "duration_min", "duration")
    c_max_depth = _maybe_col(Dive, "max_depth_m", "max_depth")
    c_avg_depth = _maybe_col(Dive, "avg_depth_m", "avg_depth")
    c_temp = _maybe_col(Dive, "temperature_c", "water_temp_c")
    c_site_rel = _maybe_col(Dive, "site")

    if c_max_depth is None:
        raise StatsServiceError(
            "Dive nema sloupec max_depth_m (ani max_depth).")

    # Seskupeni, bez filtru dle uzivatele
    q_basic = select(
        func.count(c_id),
        func.coalesce(func.sum(c_duration), 0),
        func.coalesce(func.avg(c_duration), 0.0),
        func.coalesce(func.max(c_max_depth), 0.0),
        func.coalesce(func.avg(c_avg_depth), 0.0),
        func.avg(c_temp) if c_temp is not None else None,
    )
    res = db.session.execute(q_basic).first()
    basic = {
        "dives_count": int(res[0]) if res and res[0] is not None else 0,
        "total_duration_min": float(res[1]) if res and res[1] is not None else 0.0,
        "avg_duration_min": float(res[2]) if res and res[2] is not None else 0.0,
        "max_depth_m": float(res[3]) if res and res[3] is not None else 0.0,
        "avg_depth_m": float(res[4]) if res and res[4] is not None else 0.0,
        "avg_temp_c": float(res[5]) if res and len(res) > 5 and res[5] is not None else None,
    }

    # Top lokality pro vsechny
    top_sites: List[Dict[str, Any]] = []
    Site = getattr(dive_models, "Site", None)
    if c_site_rel is not None and Site is not None and hasattr(Site, "name"):
        q_sites = (
            select(dive_models.Site.name, func.count(c_id))
            .select_from(Dive)
            .join(getattr(Dive, "site"))
            .group_by(dive_models.Site.name)
            .order_by(desc(func.count(c_id)))
            .limit(limit_top_sites)
        )
        for name, cnt in db.session.execute(q_sites).all():
            top_sites.append({"site_name": name, "dives": int(cnt)})

    # Top nejhlubbsi ponory
    top_deep_dives: List[Dict[str, Any]] = []

    # Zkusime ziskat jmeno potapece, pokud existuje relationship Dive.diver -> Diver.display_name
    has_diver_rel = hasattr(Dive, "diver")
    Diver = getattr(dive_models, "Diver", None)
    diver_has_name = Diver is not None and hasattr(Diver, "display_name")

    q_deep = (
        select(Dive)
        .order_by(desc(c_max_depth), desc(c_start if c_start is not None else c_id))
        .limit(top_deep_limit)
    )
    for d in db.session.scalars(q_deep).all():
        site_name = None
        try:
            site_obj = getattr(d, "site", None)
            site_name = getattr(
                site_obj, "name", None) if site_obj is not None else None
        except Exception:
            site_name = None

        # Jmeno potapece je volitelne, pouzijeme jen kdyz relationship existuje
        diver_name = None
        if has_diver_rel and diver_has_name:
            try:
                diver_obj = getattr(d, "diver", None)
                diver_name = getattr(
                    diver_obj, "display_name", None) if diver_obj is not None else None
            except Exception:
                diver_name = None

        dive_pk = getattr(d, "id", None) or getattr(d, "dive_id", None)

        top_deep_dives.append(
            {
                "id": int(dive_pk),
                "start_time": _safe_str(getattr(d, "start_time", None) or getattr(d, "started_at", None)),
                "max_depth_m": _to_float(getattr(d, "max_depth_m", None) or getattr(d, "max_depth", None)),
                "duration_min": _to_float(getattr(d, "duration_min", None) or getattr(d, "duration", None)),
                "site": site_name,
                "diver_name": diver_name,
            }
        )

    return {"basic": basic, "top_sites": top_sites, "top_deep_dives": top_deep_dives}
