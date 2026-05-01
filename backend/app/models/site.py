# model mista ponoru, polohy na zemi
from app.db import db


class Site(db.Model):
    __tablename__ = "site"

    site_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("app_user.user_id"),
        nullable=False,
        index=True,
    )

    name = db.Column(db.String(160), nullable=False, index=True)  # nazev mista (indexovano pro vyhledavani)
    country = db.Column(db.String(80))      # stat / zeme
    region = db.Column(db.String(80))       # region nebo kraj
    body_of_water = db.Column(db.String(80))  # vodní utvary more jezero atd
    latitude = db.Column(db.Numeric(9, 6))  # zemepisna sirka (WGS-84)
    longitude = db.Column(db.Numeric(9, 6)) # zemepisna delka (WGS-84)
    altitude_m = db.Column(db.Numeric(6, 1))  # nadmorska vyska
    description = db.Column(db.Text)
    type = db.Column(db.String(40))         # vrakov/jeskyne/utes/otevrene-more/jezero/
    current = db.Column(db.String(40))      # proud zadny/mirny/silny
    access = db.Column(db.String(40))       # pristup shore/boat/liveaboard
    website = db.Column(db.String(200))     # web stranky lokality
    photo_url = db.Column(db.String(200))   # titulni fotografie stanoviste

    dives = db.relationship("Dive", back_populates="site", lazy=True)

    def __repr__(self):
        return f"<Site user={self.user_id} {self.name}>"
