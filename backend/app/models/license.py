# model licenci uzivatele (lze priradit k ponoru)
from app.db import db
from sqlalchemy.orm import relationship


class License(db.Model):
    __tablename__ = "license"

    license_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        "app_user.user_id"), nullable=False, index=True)

    agency = db.Column(db.String(50))            # agentura PADI/SSI/CMAS/NAUI/
    certification = db.Column(db.String(80))     # nazev certifikace OWD/AOWD/Rescue/Divemaster/
    level = db.Column(db.String(80))             # volitelny stupen (1*/2*/3*)
    issued_on = db.Column(db.Date)               # datum vydani certifikace
    expires_on = db.Column(db.Date)              # datum expirace
    number = db.Column(db.String(80))            # cislo licence / certifikatu
    note = db.Column(db.Text)

    # seznam ponoru, na kterych byla tato licence pouzita
    dives = relationship("Dive", back_populates="license", lazy=True)

    def __repr__(self):
        return f"<License id={self.license_id} user={self.user_id} {self.agency or ''} {self.certification or ''}>"
