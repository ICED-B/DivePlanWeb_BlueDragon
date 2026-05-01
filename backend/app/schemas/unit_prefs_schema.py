# schema uzivatelskych preferenci jednotek
from marshmallow import Schema, fields, validate

from app.utils.enums import (
    DepthUnitEnum,
    DistanceUnitEnum,
    PressureUnitEnum,
    TemperatureUnitEnum,
    VolumeUnitEnum,
    WeightUnitEnum,
    DurationUnitEnum,
)


def _one_of_enum(enum_cls):
    return validate.OneOf([e.value for e in enum_cls])


class UnitPrefsSchema(Schema):
    # vystup cteni preferenci
    user_id = fields.Int(dump_only=True)
    depth = fields.Str(required=True, validate=_one_of_enum(DepthUnitEnum))
    distance = fields.Str(required=True, validate=_one_of_enum(DistanceUnitEnum))
    pressure = fields.Str(required=True, validate=_one_of_enum(PressureUnitEnum))
    temperature = fields.Str(required=True, validate=_one_of_enum(TemperatureUnitEnum))
    volume = fields.Str(required=True, validate=_one_of_enum(VolumeUnitEnum))
    weight = fields.Str(required=True, validate=_one_of_enum(WeightUnitEnum))
    duration = fields.Str(required=True, validate=_one_of_enum(DurationUnitEnum))


class UnitPrefsUpdateSchema(Schema):
    # pro update, dovoli poslat jen cast
    depth = fields.Str(validate=_one_of_enum(DepthUnitEnum))
    distance = fields.Str(validate=_one_of_enum(DistanceUnitEnum))
    pressure = fields.Str(validate=_one_of_enum(PressureUnitEnum))
    temperature = fields.Str(validate=_one_of_enum(TemperatureUnitEnum))
    volume = fields.Str(validate=_one_of_enum(VolumeUnitEnum))
    weight = fields.Str(validate=_one_of_enum(WeightUnitEnum))
    duration = fields.Str(validate=_one_of_enum(DurationUnitEnum))
