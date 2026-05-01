# model souboru prirazenych k ponoru
from app.db import db


class Media(db.Model):
    __tablename__ = "media"

    media_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dive_id = db.Column(db.Integer, db.ForeignKey(
        "dive.dive_id"), nullable=False, index=True)

    # kategorie souboru jako photo, video, map, doc, other
    kind = db.Column(db.String(20), nullable=False)
    uri = db.Column(db.Text, nullable=False)         # cesta nebo URL k souboru
    caption = db.Column(db.Text)                     # popis nebo nazev media

    # zpetny vztah na Dive
    dive = db.relationship("Dive", back_populates="media", lazy=True)

    def __repr__(self):
        return f"<Media id={self.media_id} dive={self.dive_id} kind={self.kind}>"
