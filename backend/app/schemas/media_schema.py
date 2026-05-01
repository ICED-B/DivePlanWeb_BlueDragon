# schema entity media val ser
from marshmallow import EXCLUDE, validate
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from app.models.media import Media
from app.db import db

class MediaSchema(SQLAlchemySchema):
    class Meta:
        model = Media
        load_instance = True
        unknown = EXCLUDE
        sqla_session = db.session

    media_id = auto_field(dump_only=True)
    dive_id = auto_field(required=True)
    kind = auto_field(required=True, validate=validate.OneOf(["photo","video","map","doc","other"]))
    uri = auto_field(required=True, validate=validate.Length(min=1))
    caption = auto_field()

class MediaCreateSchema(SQLAlchemySchema):
    class Meta:
        model = Media
        load_instance = True
        unknown = EXCLUDE
        sqla_session = db.session

    dive_id = auto_field(required=True)
    kind = auto_field(required=True, validate=validate.OneOf(["photo","video","map","doc","other"]))
    uri = auto_field(required=True, validate=validate.Length(min=1))
    caption = auto_field()

class MediaUpdateSchema(SQLAlchemySchema):
    class Meta:
        model = Media
        load_instance = False
        unknown = EXCLUDE
        sqla_session = db.session

    kind = auto_field(validate=validate.OneOf(["photo","video","map","doc","other"]))
    uri = auto_field(validate=validate.Length(min=1))
    caption = auto_field()
