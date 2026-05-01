# schema entity ExposureMetrics val ser
from marshmallow import EXCLUDE, validate, fields
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from app.models.exposure_metrics import ExposureMetrics
from app.db import db

class ExposureMetricsSchema(SQLAlchemySchema):
    class Meta:
        model = ExposureMetrics
        load_instance = True
        unknown = EXCLUDE
        sqla_session = db.session

    exposure_id = auto_field(dump_only=True)
    dive_id = auto_field(required=True)
    cns_start = fields.Float(validate=validate.Range(min=0), allow_none=True)
    cns_end = fields.Float(validate=validate.Range(min=0), allow_none=True)
    otu_start = fields.Float(validate=validate.Range(min=0), allow_none=True)
    otu_end = fields.Float(validate=validate.Range(min=0), allow_none=True)
    max_ppO2 = fields.Float(validate=validate.Range(min=0), allow_none=True)

class ExposureMetricsCreateSchema(SQLAlchemySchema):
    class Meta:
        model = ExposureMetrics
        load_instance = True
        unknown = EXCLUDE
        sqla_session = db.session

    dive_id = auto_field(required=True)
    cns_start = fields.Float(validate=validate.Range(min=0), allow_none=True)
    cns_end = fields.Float(validate=validate.Range(min=0), allow_none=True)
    otu_start = fields.Float(validate=validate.Range(min=0), allow_none=True)
    otu_end = fields.Float(validate=validate.Range(min=0), allow_none=True)
    max_ppO2 = fields.Float(validate=validate.Range(min=0), allow_none=True)

class ExposureMetricsUpdateSchema(SQLAlchemySchema):
    class Meta:
        model = ExposureMetrics
        load_instance = False
        unknown = EXCLUDE
        sqla_session = db.session

    cns_start = fields.Float(validate=validate.Range(min=0), allow_none=True)
    cns_end = fields.Float(validate=validate.Range(min=0), allow_none=True)
    otu_start = fields.Float(validate=validate.Range(min=0), allow_none=True)
    otu_end = fields.Float(validate=validate.Range(min=0), allow_none=True)
    max_ppO2 = fields.Float(validate=validate.Range(min=0), allow_none=True)
