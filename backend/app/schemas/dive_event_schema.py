# schema entity DiveEvent val ser
from marshmallow import EXCLUDE, validate, fields
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field

from app.models.dive_event import DiveEvent
from app.db import db

_event_types = validate.OneOf([
    'bookmark', 'gas_switch', 'safety_stop', 'deco_stop',
    'alarm_ascent_rate', 'alarm_ppO2_high', 'alarm_ppO2_low',
    'alarm_ceiling_violation', 'note', 'custom'
])


class DiveEventSchema(SQLAlchemySchema):
    class Meta:
        model = DiveEvent
        load_instance = True
        unknown = EXCLUDE
        sqla_session = db.session

    event_id = auto_field(dump_only=True)
    dive_id = auto_field(required=True)
    t_min = auto_field(
        required=True, validate=validate.Range(min=0))  # dříve t_sec
    type = auto_field(required=True, validate=_event_types)
    depth_m = fields.Float(validate=validate.Range(min=0), allow_none=True)
    detail = fields.Dict(allow_none=True)  # JSON objekt


class DiveEventCreateSchema(SQLAlchemySchema):
    class Meta:
        model = DiveEvent
        load_instance = True
        unknown = EXCLUDE
        sqla_session = db.session

    dive_id = auto_field(required=True)
    t_min = auto_field(required=True, validate=validate.Range(min=0))
    type = auto_field(required=True, validate=_event_types)
    depth_m = fields.Float(validate=validate.Range(min=0), allow_none=True)
    detail = fields.Dict(allow_none=True)


class DiveEventUpdateSchema(SQLAlchemySchema):
    class Meta:
        model = DiveEvent
        load_instance = False
        unknown = EXCLUDE
        sqla_session = db.session

    t_min = auto_field(validate=validate.Range(min=0))
    type = auto_field(validate=_event_types)
    depth_m = fields.Float(validate=validate.Range(min=0), allow_none=True)
    detail = fields.Dict(allow_none=True)
