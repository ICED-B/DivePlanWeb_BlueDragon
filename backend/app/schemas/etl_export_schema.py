# schema entity ETLExport
from marshmallow import EXCLUDE, validate
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from app.models.etl_export import EtlExport
from app.db import db


class EtlExportSchema(SQLAlchemySchema):
    class Meta:
        model = EtlExport
        load_instance = True
        unknown = EXCLUDE
        sqla_session = db.session

    export_id = auto_field(dump_only=True)
    user_id = auto_field(dump_only=True)
    format = auto_field(required=True, validate=validate.OneOf(["uddf", "pdf", "json", "csv"]))
    url = auto_field()
    created_at = auto_field(dump_only=True)


class EtlExportCreateSchema(SQLAlchemySchema):
    class Meta:
        model = EtlExport
        load_instance = True
        unknown = EXCLUDE
        sqla_session = db.session

    format = auto_field(required=True, validate=validate.OneOf(["uddf", "pdf", "json", "csv"]))
    url = auto_field()
