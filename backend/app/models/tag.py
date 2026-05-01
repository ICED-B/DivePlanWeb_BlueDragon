# modle tagu pro kategorizaci a oznaceni
from app.db import db
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship


class Tag(db.Model):
    __tablename__ = "tag"

    tag_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        "app_user.user_id"), nullable=False, index=True)

    name = db.Column(db.String(60), nullable=False)  # nazev stitku, Nocni, Vrak, Skola

    # seznam ponoru prirazench tomuto tagu
    dives = relationship("DiveTag", back_populates="tag", lazy=True)

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_user_tag"),  # kazdy uzivatel ma unikatni nazvy tagu
    )

    def __repr__(self):
        return f"<Tag id={self.tag_id} user={self.user_id} name={self.name}>"
