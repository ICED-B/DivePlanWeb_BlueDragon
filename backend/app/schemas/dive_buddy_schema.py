# schema entity DiveBuddy (prirazeni partaka k ponoru)
from marshmallow import EXCLUDE
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from app.models.dive_buddy import DiveBuddy
from app.db import db

class DiveBuddySchema(SQLAlchemySchema):
    class Meta:
        model = DiveBuddy
        load_instance = True
        unknown = EXCLUDE
        sqla_session = db.session

    dive_id = auto_field(required=True)
    buddy_id = auto_field(required=True)
    confirmed = auto_field()

class DiveBuddyCreateSchema(SQLAlchemySchema):
    class Meta:
        model = DiveBuddy
        load_instance = True
        unknown = EXCLUDE
        sqla_session = db.session

    dive_id = auto_field(required=True)
    buddy_id = auto_field(required=True)
    confirmed = auto_field()

class DiveBuddyUpdateSchema(SQLAlchemySchema):
    class Meta:
        model = DiveBuddy
        load_instance = False
        unknown = EXCLUDE
        sqla_session = db.session
    confirmed = auto_field()
