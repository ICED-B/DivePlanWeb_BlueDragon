# schema entity AppUser, validace a serializace dat
from marshmallow import EXCLUDE, validate, fields
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from app.models.app_user import AppUser
from app.db import db


def _fmt_dt(obj, attr):
    v = getattr(obj, attr, None)
    return v.strftime("%H:%M-%d-%m-%Y") if v else None

# schema ke cteni (admin)
class AppUserSchema(SQLAlchemySchema):
    class Meta:
        model = AppUser
        load_instance = True
        unknown = EXCLUDE
        sqla_session = db.session

    user_id = auto_field(dump_only=True)
    login = auto_field(required=True, validate=validate.Length(min=3, max=80))
    first_name = auto_field()
    last_name = auto_field()
    phone = auto_field()
    email = auto_field(validate=validate.Email())
    role = auto_field(validate=validate.OneOf(["user", "admin"]))
    is_active = auto_field()
    created_at = fields.Function(lambda obj: _fmt_dt(obj, "created_at"), dump_only=True)
    updated_at = fields.Function(lambda obj: _fmt_dt(obj, "updated_at"), dump_only=True)


class AppUserMeSchema(SQLAlchemySchema):
    # vystup pro GET uzivatele
    class Meta:
        model = AppUser
        load_instance = False
        unknown = EXCLUDE
        sqla_session = db.session

    user_id = auto_field(dump_only=True)
    login = auto_field()
    first_name = auto_field()
    last_name = auto_field()
    phone = auto_field()
    email = auto_field()
    is_active = auto_field()
    created_at = fields.Function(lambda obj: _fmt_dt(obj, "created_at"), dump_only=True)
    updated_at = fields.Function(lambda obj: _fmt_dt(obj, "updated_at"), dump_only=True)


class AppUserCreateSchema(SQLAlchemySchema):
    # pro admina POST noveho uzivatele
    class Meta:
        model = AppUser
        load_instance = False
        unknown = EXCLUDE
        sqla_session = db.session

    login = auto_field(required=True, validate=validate.Length(min=3, max=80))
    first_name = auto_field()
    last_name = auto_field()
    phone = auto_field()
    email = auto_field(validate=validate.Email())
    role = auto_field(validate=validate.OneOf(
        ["user", "admin"]), load_default="user")
    is_active = auto_field(load_default=True)
    password = fields.String(required=True, load_only=True)


class AppUserUpdateSchema(SQLAlchemySchema):
    # update existujicich zaznamu (PUT, PATCH)
    class Meta:
        model = AppUser
        load_instance = False
        unknown = EXCLUDE
        sqla_session = db.session

    login = auto_field(validate=validate.Length(min=3, max=80))
    first_name = auto_field()
    last_name = auto_field()
    phone = auto_field()
    email = auto_field(validate=validate.Email())
    role = auto_field(validate=validate.OneOf(["user", "admin"]))
    is_active = auto_field()
    password = fields.String(load_only=True)  # volitelné hashujese znovu pokud je zadano
