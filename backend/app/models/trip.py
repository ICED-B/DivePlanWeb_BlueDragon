# model vyletu, seskupuje vice ponoru do casoveho obdobi
from app.db import db
from sqlalchemy.orm import relationship


class Trip(db.Model):
    __tablename__ = "trip"

    trip_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        "app_user.user_id"), nullable=False, index=True)

    title = db.Column(db.String(120))    # nazev vyletu, Egypt 2025 Hurghada
    start_date = db.Column(db.Date)      # datum zacatku vyletu
    end_date = db.Column(db.Date)        # datum konce vyletu
    notes = db.Column(db.Text)           # volitelne poznamky k vyletu

    # seznam ponoru prirazenych k tomuto vyletu
    dives = relationship("Dive", back_populates="trip", lazy=True)

    def __repr__(self):
        return f"<Trip id={self.trip_id} user={self.user_id} title={self.title or ''}>"
