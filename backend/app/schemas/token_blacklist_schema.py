# schema TokenBlacklist
from marshmallow import EXCLUDE, fields
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from app.models.token_blacklist import TokenBlacklist
from app.db import db

class TokenBlacklistSchema(SQLAlchemySchema):
    class Meta:
        model = TokenBlacklist
        load_instance = True
        unknown = EXCLUDE
        sqla_session = db.session

    id = auto_field(dump_only=True)
    jti = auto_field(required=True)
    created_at = fields.Function(lambda obj: obj.created_at.strftime("%H:%M-%d-%m-%Y") if obj.created_at else None,dump_only=True,)
