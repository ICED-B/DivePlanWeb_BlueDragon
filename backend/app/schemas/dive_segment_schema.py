# schema entity DiveSegment val ser
from marshmallow import EXCLUDE, validate, fields
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from app.models.dive_segment import DiveSegment
from app.db import db


class DiveSegmentSchema(SQLAlchemySchema):
    class Meta:
        model = DiveSegment
        load_instance = True
        unknown = EXCLUDE
        sqla_session = db.session

    dive_segment_id = auto_field(dump_only=True)
    dive_id = auto_field(required=True)
    start_t_min = auto_field(required=True, validate=validate.Range(min=0))
    end_t_min = auto_field(validate=validate.Range(min=0))
    gas_mix_id = auto_field(allow_none=True)
    setpoint_ppO2 = fields.Float(validate=validate.Range(min=0), allow_none=True)
    note = auto_field()


class DiveSegmentCreateSchema(SQLAlchemySchema):
    class Meta:
        model = DiveSegment
        load_instance = True
        unknown = EXCLUDE
        sqla_session = db.session

    dive_id = auto_field(required=True)
    start_t_min = auto_field(required=True, validate=validate.Range(min=0))
    end_t_min = auto_field(validate=validate.Range(min=0))
    gas_mix_id = auto_field(allow_none=True)
    setpoint_ppO2 = fields.Float(validate=validate.Range(min=0), allow_none=True)
    note = auto_field()


class DiveSegmentUpdateSchema(SQLAlchemySchema):
    class Meta:
        model = DiveSegment
        load_instance = False
        unknown = EXCLUDE
        sqla_session = db.session

    start_t_min = auto_field(validate=validate.Range(min=0))
    end_t_min = auto_field(validate=validate.Range(min=0))
    gas_mix_id = auto_field(allow_none=True)
    setpoint_ppO2 = fields.Float(validate=validate.Range(min=0), allow_none=True)
    note = auto_field()
