# model expozicnich udaju u ponoru
from app.db import db
from sqlalchemy.orm import relationship


class ExposureMetrics(db.Model):
    __tablename__ = "exposure_metrics"

    exposure_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dive_id = db.Column(db.Integer, db.ForeignKey(
        "dive.dive_id"), unique=True, nullable=False)   # 1:1 vazba jeden zaznam na ponor

    cns_start = db.Column(db.Numeric(5, 2))  # CNS% na zacatku ponoru
    cns_end = db.Column(db.Numeric(5, 2))    # CNS% na konci ponoru
    otu_start = db.Column(db.Numeric(6, 1))  # OTU na zacatku ponoru
    otu_end = db.Column(db.Numeric(6, 1))    # OTU na konci ponoru (kumulativni)
    max_ppO2 = db.Column(db.Numeric(4, 2))   # maximalni parcialni tlak kysliku behem ponoru v ata

    dive = relationship("Dive", back_populates="exposure", lazy=True)

    def __repr__(self):
        return f"<Exposure dive={self.dive_id} CNS={self.cns_end}% OTU={self.otu_end}>"
