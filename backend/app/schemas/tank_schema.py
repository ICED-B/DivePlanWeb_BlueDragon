# schema entity Tank
from marshmallow import EXCLUDE, validate, fields
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from app.models.tank import Tank
from app.db import db


class TankSchema(SQLAlchemySchema):
    class Meta:
        model = Tank
        load_instance = True
        unknown = EXCLUDE
        sqla_session = db.session

    tank_id = auto_field(dump_only=True)
    user_id = auto_field(dump_only=True)
    volume_l = fields.Float(validate=validate.Range(min=0), allow_none=True)
    work_pressure_bar = fields.Float(validate=validate.Range(min=0), allow_none=True)
    material = auto_field()
    serial_number = auto_field()
    valve = auto_field()
    note = auto_field()


class TankCreateSchema(SQLAlchemySchema):
    class Meta:
        model = Tank
        load_instance = False
        unknown = EXCLUDE
        sqla_session = db.session

    volume_l = fields.Float(validate=validate.Range(min=0), allow_none=True)
    work_pressure_bar = fields.Float(validate=validate.Range(min=0), allow_none=True)
    material = auto_field()
    serial_number = auto_field()
    valve = auto_field()
    note = auto_field()


class TankUpdateSchema(SQLAlchemySchema):
    class Meta:
        model = Tank
        load_instance = False
        unknown = EXCLUDE
        sqla_session = db.session

    volume_l = fields.Float(validate=validate.Range(min=0), allow_none=True)
    work_pressure_bar = fields.Float(validate=validate.Range(min=0), allow_none=True)
    material = auto_field()
    serial_number = auto_field()
    valve = auto_field()
    note = auto_field()
