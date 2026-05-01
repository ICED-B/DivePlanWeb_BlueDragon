# Export ponoru do formatu (JSON, CSV a UDDF [XML])
# pouziva getattr fallbacky pro kompatibilitu s ruznymi variantami modelu
from __future__ import annotations

import csv
import io
import json
from datetime import datetime
from typing import Iterable, Dict, Any, Optional

from sqlalchemy import select

from app.db import db
import app.models as dive_models  # type: ignore


class ExportServiceError(Exception):
    """Vyjimka exportu, pri nenalezeni modelu nebo neplatnem vstupu."""


def _fetch_dives(
    dive_ids: Optional[Iterable[int]] = None,
    user_id: Optional[int] = None,
):
    # vraci SQLAlchemy objekty ponoru a filtruje dle dives_id nebo user_id
    # ocekava: model Dive existuje, ma PK dive_id a owner sloupec user_id
    Dive = getattr(dive_models, "Dive", None)
    if Dive is None:
        raise ExportServiceError("Model Dive nebyl nalezen.")

    stmt = select(Dive)

    # Filtrace dle vlastnika ponoru
    if user_id is not None:
        if not hasattr(Dive, "user_id"):
            raise ExportServiceError(
                "Model Dive nema sloupec user_id (po refaktoru se ocekava).")
        stmt = stmt.where(getattr(Dive, "user_id") == user_id)

    # Filtrace dle seznamu ID ponoru
    if dive_ids:
        id_attr = None
        # Hledame nazev primarniho klice (dive_id nebo id jako fallback)
        for pk_name in ("dive_id", "id"):
            if hasattr(Dive, pk_name):
                id_attr = getattr(Dive, pk_name)
                break
        if id_attr is None:
            raise ExportServiceError(
                "Model Dive nema ocekavany primarni klic dive_id ani id.")
        stmt = stmt.where(id_attr.in_(list(dive_ids)))

    return db.session.scalars(stmt).all()


def _serialize_dive(dive_obj) -> Dict[str, Any]:
    # Serializace ponoru na dict, pouziva getattr s defaulty pro kompatibilitu
    # Ziskame ID ponoru a zkusime oba mozne nazvy atributu
    dive_id = getattr(dive_obj, "dive_id", None) or getattr(
        dive_obj, "id", None)
    started_at = getattr(dive_obj, "start_time", None) or getattr(
        dive_obj, "started_at", None)
    duration_min = getattr(dive_obj, "duration_min", None) or getattr(
        dive_obj, "duration", None)
    max_depth_m = getattr(dive_obj, "max_depth_m", None) or getattr(
        dive_obj, "max_depth", None)
    avg_depth_m = getattr(dive_obj, "avg_depth_m", None) or getattr(
        dive_obj, "avg_depth", None)
    temperature_c = getattr(dive_obj, "temperature_c", None) or getattr(
        dive_obj, "water_temp_c", None)
    # Nazev lokality ziskame pres relationship (site.name)
    site = getattr(dive_obj, "site", None)
    site_name = getattr(site, "name", None) if site is not None else None

    payload = {
        "id": dive_id,
        "start_time": _isoformat(started_at),
        "duration_min": _as_float(duration_min),
        "max_depth_m": _as_float(max_depth_m),
        "avg_depth_m": _as_float(avg_depth_m),
        "temperature_c": _as_float(temperature_c),
        "site": site_name,
    }

    # Udalosti ponoru serializujeme jen kdyz relationship existuje
    if hasattr(dive_obj, "events"):
        try:
            payload["events"] = [
                {
                    "t": _isoformat(getattr(ev, "timestamp", None) or getattr(ev, "time", None)),
                    "type": getattr(ev, "type", None),
                    "depth_m": _as_float(getattr(ev, "depth_m", None) or getattr(ev, "depth", None)),
                    "note": getattr(ev, "note", None),
                }
                for ev in (getattr(dive_obj, "events") or [])
            ]
        except Exception:
            payload["events"] = []

    return payload


def _as_float(v) -> Optional[float]:    #prevod na float (pri selhani vraci none)
    try:
        if v is None:
            return None
        return float(v)
    except Exception:
        return None


def _isoformat(dt) -> Optional[str]:    # Datetime preveda na ISO 8601 a ostatni pres str()
    if dt is None:
        return None
    try:
        if isinstance(dt, datetime):
            return dt.isoformat()
        return str(dt)
    except Exception:
        return None


def export_dives_json(
    dive_ids: Optional[Iterable[int]] = None,
    user_id: Optional[int] = None,
) -> str:
    # Exportuje seznam ponoru jako JSON (UTF-8, odsazeni 2 mezery)
    dives = _fetch_dives(dive_ids, user_id)
    data = [_serialize_dive(d) for d in dives]
    return json.dumps(data, ensure_ascii=False, indent=2)


def export_dives_csv(
    dive_ids: Optional[Iterable[int]] = None,
    user_id: Optional[int] = None,
) -> str:
    # exportuje seznam jako CSV retezec
    dives = _fetch_dives(dive_ids, user_id)
    output = io.StringIO()
    writer = csv.writer(output)
    header = ["id", "start_time", "duration_min",
              "max_depth_m", "avg_depth_m", "temperature_c", "site"]
    writer.writerow(header)

    for d in dives:
        row = _serialize_dive(d)    # None hodnoty nahradime prazdnym retezcem
        writer.writerow([row.get(k, "") if row.get(
            k) is not None else "" for k in header])

    return output.getvalue()


def export_dives_uddf(
    dive_ids: Optional[Iterable[int]] = None,
    user_id: Optional[int] = None,
) -> str:
    # Export v UDDF 3.2.0 (XML)
    dives = _fetch_dives(dive_ids, user_id)

    # Hlavicka UDDF dokumentu
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<uddf version="3.2.0">',
        "  <generator>",
        "    <name>WebDivePlanner</name>",
        "    <version>1.0</version>",
        "  </generator>",
        "  <dives>",
    ]

    for d in dives:
        s = _serialize_dive(d)
        # Escapujeme ampersand v nazvu lokality (XML bezpecnost)
        # nahrazeni znaku & za nahradu &amp predelava me tim vse na text
        # tedy znaky ktere by mohly byt pouzity v payloadu jsou timto neutralizovany
        site_text = (s.get("site") or "").replace("&", "&amp;")
        lines += [
            f'    <dive id="d{s.get("id")}">',
            f'      <datetime>{s.get("start_time") or ""}</datetime>',
            f'      <duration unit="min">{s.get("duration_min") or ""}</duration>',
            f'      <maxdepth unit="m">{s.get("max_depth_m") or ""}</maxdepth>',
            f'      <avgdepth unit="m">{s.get("avg_depth_m") or ""}</avgdepth>',
            f'      <temperature unit="C">{s.get("temperature_c") or ""}</temperature>',
            f'      <site>{site_text}</site>',
        ]

        events = s.get("events") or []
        if events:
            lines.append("      <events>")
            for ev in events:
                etype = ev.get("type") or "other"
                t = ev.get("t") or ""
                depth = ev.get("depth_m")
                note = ev.get("note")
                lines.append("        <event>")
                lines.append(f"          <type>{etype}</type>")
                lines.append(f"          <time>{t}</time>")
                # Hloubka je volitelna, zapiseme jen kdyz je k dispozici
                if depth is not None:
                    lines.append(f'          <depth unit="m">{depth}</depth>')
                if note:
                    # Escapujeme ampersand i v poznamkach
                    safe_note = str(note).replace("&", "&amp;")
                    lines.append(f"          <note>{safe_note}</note>")
                lines.append("        </event>")
            lines.append("      </events>")

        lines.append("    </dive>")

    lines += [
        "  </dives>",
        "</uddf>",
    ]
    return "\n".join(lines)
