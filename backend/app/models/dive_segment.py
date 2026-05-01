# model segmentu ponoru, casovy usek s konkretnim plynem a setpointem
from app.db import db
from sqlalchemy.orm import relationship


class DiveSegment(db.Model):
    __tablename__ = "dive_segment"

    dive_segment_id = db.Column(
        db.Integer, primary_key=True, autoincrement=True)
    dive_id = db.Column(db.Integer, db.ForeignKey(
        "dive.dive_id"), nullable=False)

    start_t_min = db.Column(db.Integer, nullable=False)  # zacatek segmentu v minutach (drive start_t_sec)
    end_t_min = db.Column(db.Integer)                    # konec segmentu v minutach (drive end_t_sec)

    gas_mix_id = db.Column(db.Integer, db.ForeignKey(
        "gas_mix.gas_mix_id"), nullable=True)            # pouzivana plynova smes v tomto segmentu
    setpoint_ppO2 = db.Column(db.Numeric(4, 2))          # CCR setpoint ppO2 v ata (jen pro closed circuit)
    note = db.Column(db.Text)

    dive = relationship("Dive", back_populates="segments", lazy=True)
    gas_mix = relationship("GasMix", lazy=True)

    def __repr__(self):
        return f"<DiveSegment dive={self.dive_id} {self.start_t_min}-{self.end_t_min}min>"
