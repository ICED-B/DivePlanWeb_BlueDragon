# model udalosti behem ponoru, alarmy, poznamky, gas_switch
from app.db import db
from sqlalchemy.orm import relationship


class DiveEvent(db.Model):
    __tablename__ = "dive_event"

    event_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dive_id = db.Column(db.Integer, db.ForeignKey(
        "dive.dive_id"), nullable=False)

    t_min = db.Column(db.Integer, nullable=False)   # cas od zacatku ponoru v minutach (drive t_sec)
    # gas_switch, alarm, bookmark, note
    type = db.Column(db.String(40), nullable=False)
    depth_m = db.Column(db.Numeric(5, 2))           # hloubka v okamziku udalosti
    detail = db.Column(db.JSON)                     # typ-specificke detaily (nazev plynu pri gas_switch)

    dive = relationship("Dive", back_populates="events", lazy=True)

    def __repr__(self):
        return f"<DiveEvent dive={self.dive_id} {self.type}@{self.t_min}min>"
