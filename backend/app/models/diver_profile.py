# rozsireny profil 1:1 k AppUser, data navic pro predvolby
from app.db import db


class DiverProfile(db.Model):
    __tablename__ = "diver_profile"

    profile_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        "app_user.user_id"), unique=True, nullable=False, index=True)

    locale = db.Column(db.String(10))                       # jazykova predvolba, cs, en
    # metric / imperial  preferovana soustava jednotek
    units = db.Column(db.String(10), server_default="metric")
    sac_l_min = db.Column(db.Numeric(5, 2))                 # Surface Air Consumption v litrech za minutu
    descent_rate_m_min = db.Column(db.Numeric(5, 2))        # rychlost sestupu v m/min
    ascent_rate_m_min = db.Column(db.Numeric(5, 2))         # rychlost vystupu v m/min

    def __repr__(self):
        return f"<DiverProfile user={self.user_id}>"
