# schema entity DiveAttachment valid seria
from marshmallow import EXCLUDE, validate, fields
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field

from app.db import db
from app.models.dive_attachment import DiveAttachment


_ALLOWED_KINDS = ["photo", "pdf", "profile", "raw", "other"]


class DiveAttachmentSchema(SQLAlchemySchema):
    class Meta:
        model = DiveAttachment
        load_instance = True
        unknown = EXCLUDE
        sqla_session = db.session

    attachment_id = auto_field(dump_only=True)
    dive_id = auto_field(required=True)
    kind = auto_field(required=True, validate=validate.OneOf(_ALLOWED_KINDS))
    url = auto_field(required=True)
    note = auto_field()  # dříve caption
    created_at = fields.Function(
        lambda obj: obj.created_at.strftime("%H:%M-%d-%m-%Y") if obj.created_at else None,
        dump_only=True,
    )


class DiveAttachmentCreateSchema(SQLAlchemySchema):
    class Meta:
        model = DiveAttachment
        load_instance = True
        unknown = EXCLUDE
        sqla_session = db.session

    dive_id = auto_field(required=True)
    kind = auto_field(required=True, validate=validate.OneOf(_ALLOWED_KINDS))
    url = auto_field(required=True)
    note = auto_field()  # dříve caption
