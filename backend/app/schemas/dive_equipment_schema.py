# schema vazeb entity DiveEquipment
from marshmallow import EXCLUDE
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from app.models.dive_equipment import DiveEquipment
from app.db import db

class DiveEquipmentSchema(SQLAlchemySchema):
    class Meta:
        model = DiveEquipment
        load_instance = True
        unknown = EXCLUDE
        sqla_session = db.session

    dive_id = auto_field(required=True)
    equipment_id = auto_field(required=True)
    equipment_snapshot_json = auto_field()

class DiveEquipmentCreateSchema(SQLAlchemySchema):
    class Meta:
        model = DiveEquipment
        load_instance = True
        unknown = EXCLUDE
        sqla_session = db.session

    dive_id = auto_field(required=True)
    equipment_id = auto_field(required=True)
    equipment_snapshot_json = auto_field()
