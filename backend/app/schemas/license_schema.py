# schema entity License val ser
from marshmallow import EXCLUDE, validate
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from app.models.license import License
from app.db import db


class LicenseSchema(SQLAlchemySchema):
    class Meta:
        model = License
        load_instance = True
        unknown = EXCLUDE
        sqla_session = db.session

    license_id = auto_field(dump_only=True)
    user_id = auto_field(dump_only=True)  # owner se bere z JWT, ne z payloadu
    agency = auto_field(validate=validate.Length(max=50))
    certification = auto_field(validate=validate.Length(max=80))
    level = auto_field()
    issued_on = auto_field()
    expires_on = auto_field()
    number = auto_field(validate=validate.Length(max=80))
    note = auto_field()


class LicenseCreateSchema(SQLAlchemySchema):
    class Meta:
        model = License
        load_instance = True
        unknown = EXCLUDE
        sqla_session = db.session

    # user_id NE, nastaví route z JWT
    agency = auto_field(validate=validate.Length(max=50))
    certification = auto_field(validate=validate.Length(max=80))
    level = auto_field()
    issued_on = auto_field()
    expires_on = auto_field()
    number = auto_field(validate=validate.Length(max=80))
    note = auto_field()


class LicenseUpdateSchema(SQLAlchemySchema):
    class Meta:
        model = License
        load_instance = False
        unknown = EXCLUDE
        sqla_session = db.session

    agency = auto_field(validate=validate.Length(max=50))
    certification = auto_field(validate=validate.Length(max=80))
    level = auto_field()
    issued_on = auto_field()
    expires_on = auto_field()
    number = auto_field(validate=validate.Length(max=80))
    note = auto_field()
