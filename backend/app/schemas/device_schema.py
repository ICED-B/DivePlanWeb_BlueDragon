# schema entity device, validace a serializace
from marshmallow import EXCLUDE, validate
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from app.db import db
from app.models.device import Device


class DeviceSchema(SQLAlchemySchema):
    class Meta:
        model = Device
        load_instance = True
        unknown = EXCLUDE
        sqla_session = db.session

    device_id = auto_field(dump_only=True)
    user_id = auto_field(dump_only=True)  
    brand = auto_field(required=True, validate=validate.Length(min=2, max=80))
    model = auto_field(required=True, validate=validate.Length(min=1, max=80))
    serial_number = auto_field()
    firmware = auto_field(validate=validate.Length(max=80))
    battery_v = auto_field()
    notes = auto_field()
    hw_model_display = auto_field()
    bt_mac = auto_field()


class DeviceCreateSchema(SQLAlchemySchema):
    class Meta:
        model = Device
        load_instance = False
        unknown = EXCLUDE
        sqla_session = db.session

    brand = auto_field(required=True, validate=validate.Length(min=2, max=80))
    model = auto_field(required=True, validate=validate.Length(min=1, max=80))
    serial_number = auto_field()
    firmware = auto_field(validate=validate.Length(max=80))
    battery_v = auto_field()
    notes = auto_field()
    hw_model_display = auto_field()
    bt_mac = auto_field()


class DeviceUpdateSchema(SQLAlchemySchema):
    class Meta:
        model = Device
        load_instance = False
        unknown = EXCLUDE
        sqla_session = db.session

    brand = auto_field(validate=validate.Length(min=2, max=80))
    model = auto_field(validate=validate.Length(min=1, max=80))
    serial_number = auto_field()
    firmware = auto_field(validate=validate.Length(max=80))
    battery_v = auto_field()
    notes = auto_field()
    hw_model_display = auto_field()
    bt_mac = auto_field()
