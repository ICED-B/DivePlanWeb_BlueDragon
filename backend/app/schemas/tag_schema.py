# schema entity Tag val ser
from marshmallow import EXCLUDE, validate
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from app.models.tag import Tag
from app.db import db


class TagSchema(SQLAlchemySchema):
    class Meta:
        model = Tag
        load_instance = True
        unknown = EXCLUDE
        sqla_session = db.session

    tag_id = auto_field(dump_only=True)
    user_id = auto_field(dump_only=True)
    name = auto_field(required=True, validate=validate.Length(min=1, max=60))


class TagCreateSchema(SQLAlchemySchema):
    class Meta:
        model = Tag
        load_instance = True
        unknown = EXCLUDE
        sqla_session = db.session

    name = auto_field(required=True, validate=validate.Length(min=1, max=60))


class TagUpdateSchema(SQLAlchemySchema):
    class Meta:
        model = Tag
        load_instance = False
        unknown = EXCLUDE
        sqla_session = db.session

    name = auto_field(validate=validate.Length(min=1, max=60))
