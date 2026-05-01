# schema entity EquipmentItem val ser
from marshmallow import EXCLUDE, validate, fields
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from app.models.equipment_item import EquipmentItem
from app.db import db


class EquipmentItemSchema(SQLAlchemySchema):
    class Meta:
        model = EquipmentItem
        load_instance = True
        unknown = EXCLUDE
        sqla_session = db.session

    equipment_id = auto_field(dump_only=True)
    user_id = auto_field(dump_only=True)
    category = auto_field(required=True, validate=validate.Length(min=2, max=40))
    brand = auto_field()
    model = auto_field()
    serial_number = auto_field()
    bought_on = auto_field()
    price = fields.Float(validate=validate.Range(min=0), allow_none=True)
    state = auto_field(validate=validate.OneOf(["ok", "service", "damaged", "retired"]))
    note = auto_field()
    volume_l = fields.Float(validate=validate.Range(min=0), allow_none=True)
    work_pressure_bar = fields.Float(validate=validate.Range(min=0), allow_none=True)
    valve = auto_field()
    material = auto_field()


class EquipmentItemCreateSchema(SQLAlchemySchema):
    class Meta:
        model = EquipmentItem
        load_instance = False
        unknown = EXCLUDE
        sqla_session = db.session

    category = auto_field(required=True, validate=validate.Length(min=2, max=40))
    brand = auto_field()
    model = auto_field()
    serial_number = auto_field()
    bought_on = auto_field()
    price = fields.Float(validate=validate.Range(min=0), allow_none=True)
    state = auto_field(validate=validate.OneOf(["ok", "service", "damaged", "retired"]))
    note = auto_field()
    volume_l = fields.Float(validate=validate.Range(min=0), allow_none=True)
    work_pressure_bar = fields.Float(validate=validate.Range(min=0), allow_none=True)
    valve = auto_field()
    material = auto_field()


class EquipmentItemUpdateSchema(SQLAlchemySchema):
    class Meta:
        model = EquipmentItem
        load_instance = False
        unknown = EXCLUDE
        sqla_session = db.session

    category = auto_field(validate=validate.Length(min=2, max=40))
    brand = auto_field()
    model = auto_field()
    serial_number = auto_field()
    bought_on = auto_field()
    price = fields.Float(validate=validate.Range(min=0), allow_none=True)
    state = auto_field(validate=validate.OneOf(["ok", "service", "damaged", "retired"]))
    note = auto_field()
    volume_l = fields.Float(validate=validate.Range(min=0), allow_none=True)
    work_pressure_bar = fields.Float(validate=validate.Range(min=0), allow_none=True)
    valve = auto_field()
    material = auto_field()
