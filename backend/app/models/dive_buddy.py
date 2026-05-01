# tabulka M:N mezi ponory a spolupotapeci (kteri buddy se ucastlili ponoru)
from app.db import db
from sqlalchemy.orm import relationship


class DiveBuddy(db.Model):
    __tablename__ = "dive_buddy"

    dive_id = db.Column(db.Integer, db.ForeignKey(
        "dive.dive_id"), primary_key=True)
    buddy_id = db.Column(db.Integer, db.ForeignKey(
        "buddy.buddy_id"), primary_key=True)
    confirmed = db.Column(db.Boolean)  # volitelne potvrzeni ze strany buddyho

    dive = relationship("Dive", back_populates="buddies", lazy=True)
    buddy = relationship("Buddy", back_populates="dives", lazy=True)

    def __repr__(self):
        return f"<DiveBuddy dive={self.dive_id} buddy={self.buddy_id} confirmed={self.confirmed}>"
