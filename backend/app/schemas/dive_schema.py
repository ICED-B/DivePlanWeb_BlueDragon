# schema entity Dive val ser
from marshmallow import EXCLUDE, validate, fields
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from app.models.dive import Dive
from app.db import db

_breathing = validate.OneOf(
    ["open_circuit", "closed_circuit", "semi_closed", "apnea"])


class _TimeOnlyField(fields.DateTime):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        if hasattr(value, "strftime"):
            return value.strftime("%H:%M")
        return str(value)


class DiveSchema(SQLAlchemySchema):
    class Meta:
        model = Dive
        load_instance = True
        unknown = EXCLUDE
        sqla_session = db.session

    dive_id = auto_field(dump_only=True)
    user_id = auto_field(dump_only=True)
    trip_id = auto_field(allow_none=True)
    device_id = auto_field(allow_none=True)
    site_id = auto_field(allow_none=True)
    license_id = auto_field(allow_none=True)
    start_time = auto_field()
    duration_min = auto_field(validate=validate.Range(min=0))
    max_depth_m = fields.Float(validate=validate.Range(min=0), allow_none=True)
    avg_depth_m = fields.Float(validate=validate.Range(min=0), allow_none=True)
    surface_pressure_bar = fields.Float(allow_none=True)
    water_temp_c = fields.Float(allow_none=True)
    air_temp_c = fields.Float(allow_none=True)
    breathing_system = auto_field(required=True, validate=_breathing)
    algorithm = auto_field()
    surface_interval_min = auto_field(validate=validate.Range(min=0))
    deco_model = auto_field()
    gf_low = auto_field(validate=validate.Range(min=0, max=100))
    gf_high = auto_field(validate=validate.Range(min=0, max=100))
    ndl_min = auto_field(validate=validate.Range(min=0))
    cns_max_pct = auto_field(validate=validate.Range(min=0, max=100))
    otu = auto_field(validate=validate.Range(min=0))
    ceiling_max_m = fields.Float(validate=validate.Range(min=0), allow_none=True)
    source_meta_json = auto_field()
    notes = auto_field()


class DiveCreateSchema(SQLAlchemySchema):
    class Meta:
        model = Dive
        load_instance = False
        unknown = EXCLUDE
        sqla_session = db.session

    # user_id NE, route ho nastaví z JWT
    trip_id = auto_field(allow_none=True)
    device_id = auto_field(allow_none=True)
    site_id = auto_field(allow_none=True)
    license_id = auto_field(allow_none=True)
    start_time = auto_field(required=True)
    duration_min = auto_field(validate=validate.Range(min=0))
    max_depth_m = fields.Float(validate=validate.Range(min=0), allow_none=True)
    avg_depth_m = fields.Float(validate=validate.Range(min=0), allow_none=True)
    surface_pressure_bar = fields.Float(allow_none=True)
    water_temp_c = fields.Float(allow_none=True)
    air_temp_c = fields.Float(allow_none=True)
    breathing_system = auto_field(required=True, validate=_breathing)
    algorithm = auto_field()
    surface_interval_min = auto_field(validate=validate.Range(min=0))
    deco_model = auto_field()
    gf_low = auto_field(validate=validate.Range(min=0, max=100))
    gf_high = auto_field(validate=validate.Range(min=0, max=100))
    ndl_min = auto_field(validate=validate.Range(min=0))
    cns_max_pct = auto_field(validate=validate.Range(min=0, max=100))
    otu = auto_field(validate=validate.Range(min=0))
    ceiling_max_m = fields.Float(validate=validate.Range(min=0), allow_none=True)
    source_meta_json = auto_field()
    notes = auto_field()


class DiveUpdateSchema(SQLAlchemySchema):
    class Meta:
        model = Dive
        load_instance = False
        unknown = EXCLUDE
        sqla_session = db.session

    # user_id NE, nemění se z payloadu
    trip_id = auto_field(allow_none=True)
    device_id = auto_field(allow_none=True)
    site_id = auto_field(allow_none=True)
    license_id = auto_field(allow_none=True)
    start_time = auto_field()
    duration_min = auto_field(validate=validate.Range(min=0))
    max_depth_m = fields.Float(validate=validate.Range(min=0), allow_none=True)
    avg_depth_m = fields.Float(validate=validate.Range(min=0), allow_none=True)
    surface_pressure_bar = fields.Float(allow_none=True)
    water_temp_c = fields.Float(allow_none=True)
    air_temp_c = fields.Float(allow_none=True)
    breathing_system = auto_field(validate=_breathing)
    algorithm = auto_field()
    surface_interval_min = auto_field(validate=validate.Range(min=0))
    deco_model = auto_field()
    gf_low = auto_field(validate=validate.Range(min=0, max=100))
    gf_high = auto_field(validate=validate.Range(min=0, max=100))
    ndl_min = auto_field(validate=validate.Range(min=0))
    cns_max_pct = auto_field(validate=validate.Range(min=0, max=100))
    otu = auto_field(validate=validate.Range(min=0))
    ceiling_max_m = fields.Float(validate=validate.Range(min=0), allow_none=True)
    source_meta_json = auto_field()
    notes = auto_field()
