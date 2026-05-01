# model potapeckych partaku, udaje o spolupotapecich lze pridat k vice ponorum
from app.db import db
from sqlalchemy.orm import relationship


class Buddy(db.Model):
    __tablename__ = "buddy"

    buddy_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # vlastnik zaznamu
    user_id = db.Column(db.Integer, db.ForeignKey(
        "app_user.user_id"), nullable=False, index=True)

    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(40))
    note = db.Column(db.Text)  # volitelna poznamka (napr. certifikace, zkusenosti)

    # relationships
    dives = relationship("DiveBuddy", back_populates="buddy", lazy=True)

    def __repr__(self):
        return f"<Buddy id={self.buddy_id} user={self.user_id} name={self.name}>"
