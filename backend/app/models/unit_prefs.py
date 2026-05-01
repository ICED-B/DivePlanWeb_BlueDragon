# model preferenci jednotek uzivatele 1:1 k AppUser
from app.db import db


class UnitPrefs(db.Model):
    __tablename__ = "unit_prefs"

    # PK je zaroven FK - jeden radek na uzivatele, mazanim uzivatele se smaze i tento zaznam
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("app_user.user_id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )

    # JSON blob  {"depth":"m", "pressure":"bar", "weight":"kg", ...}
    data = db.Column(db.JSON, nullable=False, server_default="{}")

    # relationship pristup k AppUser z instance UnitPrefs
    user = db.relationship("AppUser", backref=db.backref("unit_prefs", uselist=False))

    def __repr__(self):
        return f"<UnitPrefs user_id={self.user_id}>"
