# schema entity userStats
from marshmallow import EXCLUDE, fields, validate
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from app.models.user_stats import UserStats
from app.db import db


class UserStatsSchema(SQLAlchemySchema):
    class Meta:
        model = UserStats
        load_instance = True
        unknown = EXCLUDE
        sqla_session = db.session

    user_id = auto_field(dump_only=True)
    total_dives = auto_field()
    total_hours = fields.Float(validate=validate.Range(min=0), allow_none=True)
    deepest_m = fields.Float(validate=validate.Range(min=0), allow_none=True)
    avg_depth_m = fields.Float(validate=validate.Range(min=0), allow_none=True)
    fav_site_id = auto_field(allow_none=True)
    last_dive_at = auto_field(allow_none=True)
