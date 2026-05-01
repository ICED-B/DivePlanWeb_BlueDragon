# model zaznamu o servisu vybaveni
from app.db import db


class EquipmentService(db.Model):
    __tablename__ = "equipment_service"

    service_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey("equipment_item.equipment_id"), nullable=False)

    service_type = db.Column(db.String(80))         # annual, visual, hydro, reg-service
    frequency_months = db.Column(db.Integer)        # doporuceny interval servisu v mesicich
    last_service = db.Column(db.Date)               # datum posledniho servisu
    next_service = db.Column(db.Date)               # planovane datum dalsiho servisu
    workshop = db.Column(db.String(120))            # nazev servisu nebo technika
    document_url = db.Column(db.String(300))        # URL servisniho protokolu nebo certifikatu
    note = db.Column(db.Text)

    def __repr__(self):
        return f"<EquipmentService eq={self.equipment_id} {self.service_type}>"
