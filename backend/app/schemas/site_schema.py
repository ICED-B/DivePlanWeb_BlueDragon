# schema entity Site val ser
from marshmallow import EXCLUDE, validate, fields
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from app.models.site import Site
from app.db import db

_lat = validate.Range(
    min=-90, max=90, error="latitude must be between -90 and 90")
_lon = validate.Range(
    min=-180, max=180, error="longitude must be between -180 and 180")


class SiteSchema(SQLAlchemySchema):
    class Meta:
        model = Site
        load_instance = True
        unknown = EXCLUDE
        sqla_session = db.session

    site_id = auto_field(dump_only=True)
    user_id = auto_field(dump_only=True)
    name = auto_field(required=True, validate=validate.Length(min=2, max=160))
    country = auto_field()
    region = auto_field()
    body_of_water = auto_field()
    latitude = fields.Float(validate=_lat, allow_none=True)
    longitude = fields.Float(validate=_lon, allow_none=True)
    altitude_m = fields.Float(allow_none=True)
    description = auto_field()
    type = auto_field()
    current = auto_field()
    access = auto_field()
    website = auto_field()
    photo_url = auto_field()


class SiteCreateSchema(SQLAlchemySchema):
    class Meta:
        model = Site
        load_instance = False  # user_id doplníme z JWT
        unknown = EXCLUDE
        sqla_session = db.session

    name = auto_field(required=True, validate=validate.Length(min=2, max=160))
    country = auto_field()
    region = auto_field()
    body_of_water = auto_field()
    latitude = fields.Float(validate=_lat, allow_none=True)
    longitude = fields.Float(validate=_lon, allow_none=True)
    altitude_m = fields.Float(allow_none=True)
    description = auto_field()
    type = auto_field()
    current = auto_field()
    access = auto_field()
    website = auto_field()
    photo_url = auto_field()


class SiteUpdateSchema(SQLAlchemySchema):
    class Meta:
        model = Site
        load_instance = False
        unknown = EXCLUDE
        sqla_session = db.session

    name = auto_field(validate=validate.Length(min=2, max=160))
    country = auto_field()
    region = auto_field()
    body_of_water = auto_field()
    latitude = fields.Float(validate=_lat, allow_none=True)
    longitude = fields.Float(validate=_lon, allow_none=True)
    altitude_m = fields.Float(allow_none=True)
    description = auto_field()
    type = auto_field()
    current = auto_field()
    access = auto_field()
    website = auto_field()
    photo_url = auto_field()
