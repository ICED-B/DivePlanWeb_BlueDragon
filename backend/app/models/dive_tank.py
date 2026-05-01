# model lahve pouzite pro ponor
from app.db import db
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship


class DiveTank(db.Model):
    __tablename__ = "dive_tank"

    dive_tank_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dive_id = db.Column(db.Integer, db.ForeignKey("dive.dive_id"), nullable=False)
    tank_id = db.Column(db.Integer, db.ForeignKey("tank.tank_id"), nullable=True)       # odkaz na katalogovou lahev
    gas_mix_id = db.Column(db.Integer, db.ForeignKey("gas_mix.gas_mix_id"), nullable=True)  # plynova smes v lahvi

    start_pressure_bar = db.Column(db.Numeric(6, 1))   # tlak pri vstupu do vody
    end_pressure_bar = db.Column(db.Numeric(6, 1))     # tlak po vynoreni
    position = db.Column(db.String(40))                # backmount_left/right, stage, bailout, ...

    dive = relationship("Dive", back_populates="tanks", lazy=True)
    tank = relationship("Tank", lazy=True)
    gas_mix = relationship("GasMix", lazy=True)

    __table_args__ = (
        UniqueConstraint("dive_id", "tank_id", name="uq_dive_tank_once_per_dive"),  # stejna lahev max jednou na ponor
    )

    def __repr__(self):
        return f"<DiveTank dive={self.dive_id} tank={self.tank_id} gas={self.gas_mix_id}>"
