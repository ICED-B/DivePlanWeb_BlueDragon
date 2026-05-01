# schema entity ProfileSample val ser
from marshmallow import EXCLUDE, validate, fields
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field

from app.models.profile_sample import ProfileSample
from app.db import db


class ProfileSampleSchema(SQLAlchemySchema):
    class Meta:
        model = ProfileSample
        load_instance = True
        unknown = EXCLUDE
        sqla_session = db.session

    sample_id = auto_field(dump_only=True)
    dive_id = auto_field(required=True)
    t_min = auto_field(required=True, validate=validate.Range(min=0))
    depth_m = fields.Float(required=True, validate=validate.Range(min=0))
    temp_c = fields.Float(allow_none=True)
    ndl_min = auto_field(validate=validate.Range(min=0))
    ceilings_m = fields.Float(validate=validate.Range(min=0), allow_none=True)
    ascent_rate_mpm = fields.Float(allow_none=True)
    tank_pressure_bar = fields.Float(validate=validate.Range(min=0), allow_none=True)
    ppO2 = fields.Float(validate=validate.Range(min=0), allow_none=True)
    setpoint_o2 = fields.Float(validate=validate.Range(min=0), allow_none=True)
    ceiling_m = fields.Float(validate=validate.Range(min=0), allow_none=True)


class ProfileSampleCreateSchema(SQLAlchemySchema):
    class Meta:
        model = ProfileSample
        load_instance = True
        unknown = EXCLUDE
        sqla_session = db.session

    dive_id = auto_field(required=True)
    t_min = auto_field(required=True, validate=validate.Range(min=0))
    depth_m = fields.Float(required=True, validate=validate.Range(min=0))
    temp_c = fields.Float(allow_none=True)
    ndl_min = auto_field(validate=validate.Range(min=0))
    ceilings_m = fields.Float(validate=validate.Range(min=0), allow_none=True)
    ascent_rate_mpm = fields.Float(allow_none=True)
    tank_pressure_bar = fields.Float(validate=validate.Range(min=0), allow_none=True)
    ppO2 = fields.Float(validate=validate.Range(min=0), allow_none=True)
    setpoint_o2 = fields.Float(validate=validate.Range(min=0), allow_none=True)
    ceiling_m = fields.Float(validate=validate.Range(min=0), allow_none=True)


class ProfileSampleUpdateSchema(SQLAlchemySchema):
    class Meta:
        model = ProfileSample
        load_instance = False
        unknown = EXCLUDE
        sqla_session = db.session

    t_min = auto_field(validate=validate.Range(min=0))
    depth_m = fields.Float(validate=validate.Range(min=0))
    temp_c = fields.Float(allow_none=True)
    ndl_min = auto_field(validate=validate.Range(min=0))
    ceilings_m = fields.Float(validate=validate.Range(min=0), allow_none=True)
    ascent_rate_mpm = fields.Float(allow_none=True)
    tank_pressure_bar = fields.Float(validate=validate.Range(min=0), allow_none=True)
    ppO2 = fields.Float(validate=validate.Range(min=0), allow_none=True)
    setpoint_o2 = fields.Float(validate=validate.Range(min=0), allow_none=True)
    ceiling_m = fields.Float(validate=validate.Range(min=0), allow_none=True)
