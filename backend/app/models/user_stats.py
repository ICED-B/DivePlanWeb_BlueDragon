# model statistik uzivatele 1:1 k AppUser
from app.db import db


class UserStats(db.Model):
    __tablename__ = "user_stats"

    # 1:1 - PK je zaroven FK, coz zajistuje max jeden zaznam na uzivatele
    user_id = db.Column(db.Integer, db.ForeignKey(
        "app_user.user_id"), primary_key=True)

    total_dives = db.Column(db.Integer)              # celkovy pocet zaznamenych ponoru
    total_hours = db.Column(db.Numeric(6, 2))        # celkovy cas pod vodou v hodinach
    deepest_m = db.Column(db.Numeric(5, 1))          # nejhlubsi dosazena hloubka v metrech
    avg_depth_m = db.Column(db.Numeric(5, 1))        # prumerna hloubka pres vsechny ponory
    fav_site_id = db.Column(db.Integer, db.ForeignKey("site.site_id"))  # nejcasteji navstivene stanoviste
    last_dive_at = db.Column(db.DateTime(timezone=True))  # cas posledniho ponoru

    def __repr__(self):
        return f"<UserStats user={self.user_id} dives={self.total_dives}>"
