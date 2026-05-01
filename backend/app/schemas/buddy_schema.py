# schema entity Buddy, validace a serializace
from marshmallow import EXCLUDE, validate
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from app.models.buddy import Buddy
from app.db import db

_phone_rx = validate.Regexp(r"^\+?[\d\s\-]{6,}$")


class BuddySchema(SQLAlchemySchema):
    class Meta:
        model = Buddy
        load_instance = True
        unknown = EXCLUDE
        sqla_session = db.session

    buddy_id = auto_field(dump_only=True)
    user_id = auto_field(dump_only=True)
    name = auto_field(required=True, validate=validate.Length(min=2, max=120))
    email = auto_field(validate=validate.Email())
    phone = auto_field(validate=_phone_rx)
    note = auto_field()


class BuddyCreateSchema(SQLAlchemySchema):
    class Meta:
        model = Buddy
        load_instance = True
        unknown = EXCLUDE
        sqla_session = db.session

    name = auto_field(required=True, validate=validate.Length(min=2, max=120))
    email = auto_field(validate=validate.Email())
    phone = auto_field(validate=_phone_rx)
    note = auto_field()


class BuddyUpdateSchema(SQLAlchemySchema):
    class Meta:
        model = Buddy
        load_instance = False
        unknown = EXCLUDE
        sqla_session = db.session

    name = auto_field(validate=validate.Length(min=2, max=120))
    email = auto_field(validate=validate.Email())
    phone = auto_field(validate=_phone_rx)
    note = auto_field()
