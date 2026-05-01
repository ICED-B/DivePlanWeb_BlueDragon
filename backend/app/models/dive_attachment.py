# model prilohy k ponorum, URL odkaz na soubor ulozeny mimo DB (prilohy)
from app.db import db


class DiveAttachment(db.Model):
    __tablename__ = "dive_attachment"

    attachment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dive_id = db.Column(db.Integer, db.ForeignKey(
        "dive.dive_id"), nullable=False)

    # photo/pdf/profile/raw/other - kategorie prilohy
    kind = db.Column(db.String(20), nullable=False)
    url = db.Column(db.Text, nullable=False)  # absolutni nebo relativni URL souboru
    note = db.Column(db.Text)                 # popis prilohy (drive caption)

    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=db.func.now())

    dive = db.relationship("Dive", back_populates="attachments")

    def __repr__(self):
        return f"<DiveAttachment dive={self.dive_id} kind={self.kind}>"
