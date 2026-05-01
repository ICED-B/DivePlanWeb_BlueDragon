# model potapeckeho pocitace uzivatele, lze priradit k ponorum
from app.db import db


class Device(db.Model):
    __tablename__ = "device"

    device_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # user-owned katalog zarizeni
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("app_user.user_id"),
        nullable=False,
        index=True,
    )

    # Suunto, Shearwater, Garmin, ...
    brand = db.Column(db.String(80), nullable=False)
    # Zoop Novo, Peregrine, Descent Mk2, ...
    model = db.Column(db.String(80), nullable=False)
    serial_number = db.Column(db.String(80), unique=False)  # SN neni globalne unikatni (ruzni vyrobci)
    firmware = db.Column(db.String(80))                     # verze firmware zarizeni
    battery_v = db.Column(db.Numeric(4, 2))                 # napeti baterie v voltech
    notes = db.Column(db.Text)

    # volitelna metadata z importu (napr. ze Subsurface/DiveComputer)
    hw_model_display = db.Column(db.String(80))  # zobrazovany nazev HW modelu
    bt_mac = db.Column(db.String(50))            # Bluetooth MAC adresa pro sparovani

    # relationships
    dives = db.relationship("Dive", back_populates="device", lazy=True)

    def __repr__(self):
        return f"<Device id={self.device_id} user={self.user_id} {self.brand} {self.model} SN={self.serial_number}>"
