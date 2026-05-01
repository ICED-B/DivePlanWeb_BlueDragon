# model audit logu, zaznam o akcich (kdo co kdy provedl)
from app.db import db


class AuditLog(db.Model):
    __tablename__ = "audit_log"

    audit_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # koho se akce tyka (owner dat / ucet)
    user_id = db.Column(db.Integer, db.ForeignKey(
        "app_user.user_id"), nullable=True, index=True)

    # LOGIN/IMPORT/EXPORT/UPDATE/DELETE/...
    action = db.Column(db.String(40), nullable=False)
    entity = db.Column(db.String(60))               # nazev entity (napr. "dive", "user")
    entity_id = db.Column(db.String(60))            # ID dotcene entity jako retezec
    changes_json = db.Column(db.JSON)               # diff pred/po zmene
    reason = db.Column(db.Text)                     # duvod akce

    # kdo akci provedl (typicky stejny jako user_id, ale u admin operaci muze byt jiny)
    performed_by = db.Column(db.Integer, db.ForeignKey(
        "app_user.user_id"), nullable=True, index=True)

    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=db.func.now())

    def __repr__(self):
        return f"<Audit id={self.audit_id} action={self.action} entity={self.entity}:{self.entity_id}>"
