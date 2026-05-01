# schema detailu ponoru
from marshmallow_sqlalchemy import SQLAlchemySchema
from marshmallow import EXCLUDE, fields
from app.db import db
from app.models.dive import Dive
from app.schemas.dive_schema import DiveSchema
from app.schemas.dive_tank_schema import DiveTankSchema
from app.schemas.dive_segment_schema import DiveSegmentSchema
from app.schemas.profile_sample_schema import ProfileSampleSchema
from app.schemas.dive_event_schema import DiveEventSchema

class DiveDetailSchema(DiveSchema):
    #cteci schema ponrou pro detaily
    class Meta(DiveSchema.Meta):
        # DiveSchema already sets model, load_instance, unknown, sqla_session
        pass

    # nested collections (dump-only)
    tanks = fields.List(fields.Nested(DiveTankSchema), dump_only=True)
    segments = fields.List(fields.Nested(DiveSegmentSchema), dump_only=True)
    samples = fields.List(fields.Nested(ProfileSampleSchema), dump_only=True)
    events = fields.List(fields.Nested(DiveEventSchema), dump_only=True)
