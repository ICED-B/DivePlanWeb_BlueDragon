# schema entity ETLImport
from marshmallow import EXCLUDE, validate
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from app.models.etl_import import EtlImport
from app.db import db


class EtlImportSchema(SQLAlchemySchema):
    class Meta:
        model = EtlImport
        load_instance = True
        unknown = EXCLUDE
        sqla_session = db.session

    import_id = auto_field(dump_only=True)
    user_id = auto_field(dump_only=True)
    source = auto_field(required=True, validate=validate.OneOf(["uddf", "suunto_xml", "sml", "sde", "csv", "json", "pdf"]))
    filename = auto_field()
    status = auto_field(validate=validate.OneOf(["ok", "failed", "partial"]))
    log = auto_field()
    checksum = auto_field()
    raw_path = auto_field()
    created_at = auto_field(dump_only=True)


class EtlImportCreateSchema(SQLAlchemySchema):
    class Meta:
        model = EtlImport
        load_instance = True
        unknown = EXCLUDE
        sqla_session = db.session

    source = auto_field(required=True, validate=validate.OneOf(["uddf", "suunto_xml", "sml", "sde", "csv", "json", "pdf"]))
    filename = auto_field()
    status = auto_field(validate=validate.OneOf(["ok", "failed", "partial"]))
    log = auto_field()
    checksum = auto_field()
    raw_path = auto_field()
