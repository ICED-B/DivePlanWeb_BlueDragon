# model vzorku profilu ponoru
from app.db import db
from sqlalchemy.orm import relationship


class ProfileSample(db.Model):
    __tablename__ = "profile_sample"

    sample_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dive_id = db.Column(db.Integer, db.ForeignKey(
        "dive.dive_id"), nullable=False)

    # cas od zacatku ponoru v minutach (drive t_sec v sekundach)
    t_min = db.Column(db.Integer, nullable=False)
    depth_m = db.Column(db.Numeric(5, 2), nullable=False)  # aktualni hloubka v metrech
    temp_c = db.Column(db.Numeric(5, 2))                   # teplota vody

    ndl_min = db.Column(db.Integer)                        # zbyvajici NDL v minutach (drive ndl_sec)
    ceilings_m = db.Column(db.Numeric(5, 2))               # deko strop z pocitace (historicke pole)
    ascent_rate_mpm = db.Column(db.Numeric(6, 2))          # okamzita rychlost vystupu v m/min
    tank_pressure_bar = db.Column(db.Numeric(6, 2))        # tlak v lahvi v okamziku vzorku
    ppO2 = db.Column(db.Numeric(4, 2))                     # parcialni tlak O2 v ata (drive po2)
    setpoint_o2 = db.Column(db.Numeric(4, 2))              # CCR setpoint ppO2 v ata
    ceiling_m = db.Column(db.Numeric(5, 2))                # deko strop z pocitace v metrech (sjednocene pole)

    dive = relationship("Dive", back_populates="samples", lazy=True)

    def __repr__(self):
        return f"<ProfileSample dive={self.dive_id} t={self.t_min}min depth={self.depth_m}m>"
