# asociacni tabulka M:N mezi ponorem a vybavenim (kde bylo co vyuzito)
from app.db import db


class DiveEquipment(db.Model):
    __tablename__ = "dive_equipment"

    dive_id = db.Column(db.Integer, db.ForeignKey(
        "dive.dive_id"), primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey(
        "equipment_item.equipment_id"), primary_key=True)
    # volitelne: ulozit parametry vybaveni v case ponoru (napr. tlak lahve, firmware pocitace)
    equipment_snapshot_json = db.Column(db.JSON)

    dive = db.relationship("Dive", back_populates="equipment")

    def __repr__(self):
        return f"<DiveEquipment dive={self.dive_id} eq={self.equipment_id}>"
