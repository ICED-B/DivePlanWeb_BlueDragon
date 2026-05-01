# schema entity DiveTank
from marshmallow import EXCLUDE, validate, fields
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from app.models.dive_tank import DiveTank
from app.db import db

class DiveTankSchema(SQLAlchemySchema):
    class Meta:
        model = DiveTank
        load_instance = True
        unknown = EXCLUDE
        sqla_session = db.session

    dive_tank_id = auto_field(dump_only=True)
    dive_id = auto_field(required=True)
    tank_id = auto_field(allow_none=True)
    gas_mix_id = auto_field(allow_none=True)
    start_pressure_bar = fields.Float(validate=validate.Range(min=0), allow_none=True)
    end_pressure_bar = fields.Float(validate=validate.Range(min=0), allow_none=True)
    position = auto_field()

class DiveTankCreateSchema(SQLAlchemySchema):
    class Meta:
        model = DiveTank
        load_instance = True
        unknown = EXCLUDE
        sqla_session = db.session

    dive_id = auto_field(required=True)
    tank_id = auto_field(allow_none=True)
    gas_mix_id = auto_field(allow_none=True)
    start_pressure_bar = fields.Float(validate=validate.Range(min=0), allow_none=True)
    end_pressure_bar = fields.Float(validate=validate.Range(min=0), allow_none=True)
    position = auto_field()

class DiveTankUpdateSchema(SQLAlchemySchema):
    class Meta:
        model = DiveTank
        load_instance = False
        unknown = EXCLUDE
        sqla_session = db.session

    tank_id = auto_field(allow_none=True)
    gas_mix_id = auto_field(allow_none=True)
    start_pressure_bar = fields.Float(validate=validate.Range(min=0), allow_none=True)
    end_pressure_bar = fields.Float(validate=validate.Range(min=0), allow_none=True)
    position = auto_field()
