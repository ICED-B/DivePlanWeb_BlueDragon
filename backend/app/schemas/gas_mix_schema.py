# schema entity GasMix val ser
from marshmallow import EXCLUDE, validate, fields, Schema
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from app.models.gas_mix import GasMix
from app.db import db

_percent = validate.Range(min=0, max=100, error="percent must be 0..100")


class GasMixSchema(SQLAlchemySchema):
    class Meta:
        model = GasMix
        load_instance = True
        unknown = EXCLUDE
        sqla_session = db.session

    gas_mix_id = auto_field(dump_only=True)
    user_id = auto_field(dump_only=True)
    gas_type = auto_field(required=True, validate=validate.OneOf(['air', 'nitrox', 'trimix', 'heliox', 'other']))
    o2_percent = fields.Float(validate=_percent, allow_none=True)
    he_percent = fields.Float(validate=_percent, allow_none=True)
    active = auto_field()
    name = auto_field()


class GasMixCreateSchema(SQLAlchemySchema):
    class Meta:
        model = GasMix
        load_instance = False
        unknown = EXCLUDE
        sqla_session = db.session

    gas_type = auto_field(required=True, validate=validate.OneOf(['air', 'nitrox', 'trimix', 'heliox', 'other']))
    o2_percent = fields.Float(validate=_percent, allow_none=True)
    he_percent = fields.Float(validate=_percent, allow_none=True)
    name = auto_field()


class GasMixUpdateSchema(SQLAlchemySchema):
    class Meta:
        model = GasMix
        load_instance = False
        unknown = EXCLUDE
        sqla_session = db.session

    gas_type = auto_field(validate=validate.OneOf(['air', 'nitrox', 'trimix', 'heliox', 'other']))
    o2_percent = fields.Float(validate=_percent, allow_none=True)
    he_percent = fields.Float(validate=_percent, allow_none=True)
    active = auto_field()
    name = auto_field()


class GasCalcModIn(Schema):
    o2_percent = fields.Float(required=False)
    fo2 = fields.Float(required=False)     # 0.32
    ppO2 = fields.Float(required=False)    # default 1.4


class GasCalcModOut(Schema):
    o2_percent = fields.Float(required=True)
    ppO2 = fields.Float(required=True)
    mod_m = fields.Float(required=True)


class GasCalcBestMixIn(Schema):
    depth_m = fields.Float(required=True)
    ppO2 = fields.Float(required=False)


class GasCalcBestMixOut(Schema):
    depth_m = fields.Float(required=True)
    ppO2 = fields.Float(required=True)
    o2_percent = fields.Float(required=True)


class GasCalcEadIn(Schema):
    depth_m = fields.Float(required=True)
    o2_percent = fields.Float(required=False)
    fo2 = fields.Float(required=False)


class GasCalcEadOut(Schema):
    depth_m = fields.Float(required=True)
    o2_percent = fields.Float(required=True)
    ead_m = fields.Float(required=True)
