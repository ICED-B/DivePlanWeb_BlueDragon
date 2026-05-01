# schmema pro entitu AutditLog, serializace zaznamu
from marshmallow import EXCLUDE, fields
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from app.models.audit_log import AuditLog
from app.db import db


class AuditLogSchema(SQLAlchemySchema):
    # pro cteni zaznamu
    class Meta:
        model = AuditLog
        load_instance = True
        unknown = EXCLUDE
        sqla_session = db.session

    audit_id = auto_field(dump_only=True)
    user_id = auto_field(allow_none=True)
    action = auto_field(required=True)
    entity = auto_field()
    entity_id = auto_field()
    changes_json = auto_field()
    reason = auto_field()

    performed_by = auto_field(dump_only=True)
    created_at = fields.Function(
        lambda obj: obj.created_at.strftime("%H:%M-%d-%m-%Y") if obj.created_at else None,
        dump_only=True,
    )
