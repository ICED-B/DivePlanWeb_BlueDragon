# schema entity Trip
from marshmallow import EXCLUDE, validate
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from app.models.trip import Trip
from app.db import db


class TripSchema(SQLAlchemySchema):
    class Meta:
        model = Trip
        load_instance = True
        unknown = EXCLUDE
        sqla_session = db.session

    trip_id = auto_field(dump_only=True)
    user_id = auto_field(dump_only=True)
    title = auto_field(validate=validate.Length(max=120))
    start_date = auto_field()
    end_date = auto_field()
    notes = auto_field()


class TripCreateSchema(SQLAlchemySchema):
    class Meta:
        model = Trip
        load_instance = False
        unknown = EXCLUDE
        sqla_session = db.session

    title = auto_field(validate=validate.Length(max=120))
    start_date = auto_field()
    end_date = auto_field()
    notes = auto_field()


class TripUpdateSchema(SQLAlchemySchema):
    class Meta:
        model = Trip
        load_instance = False
        unknown = EXCLUDE
        sqla_session = db.session

    title = auto_field(validate=validate.Length(max=120))
    start_date = auto_field()
    end_date = auto_field()
    notes = auto_field()
