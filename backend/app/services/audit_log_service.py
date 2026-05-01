# Sluzba pro zapis zaznamu do autid logu
# Zajistuje ze selhani zapisu nenarusi hlavni akci kteru se provadi
from __future__ import annotations

from typing import Any, Optional, Dict
from app.db import db
from app.models.audit_log import AuditLog


def write_audit(
    *,
    user_id: Optional[int],
    action: str,
    entity: Optional[str] = None,
    entity_id: Optional[str] = None,
    changes: Optional[Dict[str, Any]] = None,
    reason: Optional[str] = None,
    performed_by: Optional[int] = None,
) -> None:

    # Zapise audit log a nikdy nevyhazuje chybu ven
    print("AUDIT WRITE CALLED:", action, user_id)
    try:
        obj = AuditLog(
            user_id=user_id,
            action=action,
            entity=entity,
            # entity_id ulozime vzdy jako retezec, nebo None
            entity_id=str(entity_id) if entity_id is not None else None,
            changes_json=changes,
            reason=reason,
            performed_by=performed_by,
        )
        db.session.add(obj)
        db.session.commit()
        print("AUDIT WRITE OK:", obj.audit_id)
    except Exception as e:
        db.session.rollback()
        print("AUDIT WRITE FAILED:", repr(e))
        # audit nesmi shodit login/registraci apod.
        return
