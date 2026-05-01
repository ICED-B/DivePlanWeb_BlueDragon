# schema entity DiverProfile val ser
from marshmallow import EXCLUDE, validate
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from app.models.diver_profile import DiverProfile
from app.db import db


class DiverProfileSchema(SQLAlchemySchema):
    class Meta:
        model = DiverProfile
        load_instance = True
        unknown = EXCLUDE
        sqla_session = db.session

    profile_id = auto_field(dump_only=True)
    user_id = auto_field(dump_only=True)

    locale = auto_field(validate=validate.Length(max=10))
    units = auto_field(validate=validate.OneOf(["metric", "imperial"]))
    sac_l_min = auto_field()
    descent_rate_m_min = auto_field()
    ascent_rate_m_min = auto_field()


class DiverProfileCreateSchema(SQLAlchemySchema):
    class Meta:
        model = DiverProfile
        load_instance = True
        unknown = EXCLUDE
        sqla_session = db.session

    locale = auto_field(validate=validate.Length(max=10))
    units = auto_field(validate=validate.OneOf(["metric", "imperial"]))
    sac_l_min = auto_field()
    descent_rate_m_min = auto_field()
    ascent_rate_m_min = auto_field()


class DiverProfileUpdateSchema(SQLAlchemySchema):
    class Meta:
        model = DiverProfile
        load_instance = False
        unknown = EXCLUDE
        sqla_session = db.session

    locale = auto_field(validate=validate.Length(max=10))
    units = auto_field(validate=validate.OneOf(["metric", "imperial"]))
    sac_l_min = auto_field()
    descent_rate_m_min = auto_field()
    ascent_rate_m_min = auto_field()
