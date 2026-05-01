# model lahvi uzivatele
from app.db import db


class Tank(db.Model):
    __tablename__ = "tank"

    tank_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("app_user.user_id"),
        nullable=False,
        index=True,
    )

    volume_l = db.Column(db.Numeric(5, 2))           # vnitrni objem lahve v litrech (12.0, 15.0)
    work_pressure_bar = db.Column(db.Numeric(6, 1))  # maximalni pracovni tlak v barech (200, 232, 300)
    material = db.Column(db.String(40))              # material steel/alu
    serial_number = db.Column(db.String(80))         # seriove cislo lahve pro identifikaci
    valve = db.Column(db.String(40))                 # typ ventilu 1_ventil/2_ventil/stage/twinset
    note = db.Column(db.Text)

    def __repr__(self):
        return f"<Tank user={self.user_id} {self.volume_l}L/{self.work_pressure_bar}bar>"
