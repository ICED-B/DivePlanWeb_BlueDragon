# model potapeckeho vybaveni (pokryva veskerou vybavu az na PC)
from app.db import db


class EquipmentItem(db.Model):
    __tablename__ = "equipment_item"

    equipment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # vlastnik vybaveni
    user_id = db.Column(db.Integer, db.ForeignKey(
        "app_user.user_id"), nullable=False, index=True)

    # bcd, reg, suit, light, tank, computer
    category = db.Column(db.String(40), nullable=False)
    brand = db.Column(db.String(80))
    model = db.Column(db.String(80))
    serial_number = db.Column(db.String(80))
    bought_on = db.Column(db.Date)                  # datum nakupu
    price = db.Column(db.Numeric(10, 2))            # porizovaci cena
    state = db.Column(db.String(20), nullable=False,
                      server_default="ok")          # stav vybaveni ok/service/damaged/retired
    note = db.Column(db.Text)

    # dalsi sloupce jen pro lahve (category = 'tank')
    volume_l = db.Column(db.Numeric(5, 2))          # vnitrni objem lahve v litrech
    work_pressure_bar = db.Column(db.Numeric(6, 1)) # pracovni tlak lahve v barech
    valve = db.Column(db.String(40))                # 1_ventil/2_ventil/stage/twinset
    material = db.Column(db.String(40))             # material lahve steel/alu

    def __repr__(self):
        return f"<EquipmentItem id={self.equipment_id} user={self.user_id} cat={self.category}>"
