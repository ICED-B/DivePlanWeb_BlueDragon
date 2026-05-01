# asociacni tabulka M:N mezi ponorem a tagem (umoznuje kategorizaci)
from app.db import db
from sqlalchemy.orm import relationship


class DiveTag(db.Model):
    __tablename__ = "dive_tag"

    dive_id = db.Column(db.Integer, db.ForeignKey(
        "dive.dive_id"), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey(
        "tag.tag_id"), primary_key=True)

    dive = relationship("Dive", back_populates="tags", lazy=True)
    tag = relationship("Tag", back_populates="dives", lazy=True)

    def __repr__(self):
        return f"<DiveTag dive={self.dive_id} tag={self.tag_id}>"
