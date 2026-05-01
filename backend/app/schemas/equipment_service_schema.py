# schema entity EquipmentService
from marshmallow import EXCLUDE, validate
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from app.models.equipment_service import EquipmentService
from app.db import db

class EquipmentServiceSchema(SQLAlchemySchema):
    class Meta:
        model = EquipmentService
        load_instance = True
        unknown = EXCLUDE
        sqla_session = db.session

    service_id = auto_field(dump_only=True)
    equipment_id = auto_field(required=True)
    service_type = auto_field()
    frequency_months = auto_field(validate=validate.Range(min=0))
    last_service = auto_field()
    next_service = auto_field()
    workshop = auto_field()
    document_url = auto_field()
    note = auto_field()

class EquipmentServiceCreateSchema(SQLAlchemySchema):
    class Meta:
        model = EquipmentService
        load_instance = True
        unknown = EXCLUDE
        sqla_session = db.session

    equipment_id = auto_field(required=True)
    service_type = auto_field()
    frequency_months = auto_field(validate=validate.Range(min=0))
    last_service = auto_field()
    next_service = auto_field()
    workshop = auto_field()
    document_url = auto_field()
    note = auto_field()

class EquipmentServiceUpdateSchema(SQLAlchemySchema):
    class Meta:
        model = EquipmentService
        load_instance = False
        unknown = EXCLUDE
        sqla_session = db.session

    service_type = auto_field()
    frequency_months = auto_field(validate=validate.Range(min=0))
    last_service = auto_field()
    next_service = auto_field()
    workshop = auto_field()
    document_url = auto_field()
    note = auto_field()
