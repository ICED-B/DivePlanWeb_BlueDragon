# schema entity DiveTag
from marshmallow import EXCLUDE
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from app.models.dive_tag import DiveTag
from app.db import db

class DiveTagSchema(SQLAlchemySchema):
    class Meta:
        model = DiveTag
        load_instance = True
        unknown = EXCLUDE
        sqla_session = db.session

    dive_id = auto_field(required=True)
    tag_id = auto_field(required=True)

class DiveTagCreateSchema(SQLAlchemySchema):
    class Meta:
        model = DiveTag
        load_instance = True
        unknown = EXCLUDE
        sqla_session = db.session

    dive_id = auto_field(required=True)
    tag_id = auto_field(required=True)
