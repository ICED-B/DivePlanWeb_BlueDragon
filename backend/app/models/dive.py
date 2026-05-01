# hlavni model ponoru pro zaznam v deniku, obsahuje veliciny a FK na site, trip, device a license
from app.db import db
from sqlalchemy import CheckConstraint
from sqlalchemy.orm import relationship


class Dive(db.Model):
    __tablename__ = "dive"

    dive_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # vlastnik zaznamu (AppUser)
    user_id = db.Column(db.Integer, db.ForeignKey(
        "app_user.user_id"), nullable=False, index=True)
    # ostatni FK
    license_id = db.Column(db.Integer, db.ForeignKey(
        "license.license_id"), nullable=True)
    trip_id = db.Column(db.Integer, db.ForeignKey(
        "trip.trip_id"), nullable=True)
    device_id = db.Column(db.Integer, db.ForeignKey(
        "device.device_id"), nullable=True)
    site_id = db.Column(db.Integer, db.ForeignKey(
        "site.site_id"), nullable=True)

    start_time = db.Column(db.DateTime(timezone=True), nullable=False)  # cas startu ponoru
    duration_min = db.Column(db.Integer)                                # celkova doba ponoru v min
    max_depth_m = db.Column(db.Numeric(5, 2))                           # max hloubka v metrech
    avg_depth_m = db.Column(db.Numeric(5, 2))                           # prum hloubka v m
    surface_pressure_bar = db.Column(db.Numeric(6, 3))                  # tlak na hladine
    water_temp_c = db.Column(db.Numeric(5, 2))                          # teplota vody
    air_temp_c = db.Column(db.Numeric(5, 2))                            # teplota vzduchu
    breathing_system = db.Column(
        db.String(20), nullable=False, server_default="open_circuit")   # open_circuit/ccr/scr
    algorithm = db.Column(db.String(80))                                # dekompresni algoritmus (Buhlmann ZHL-16C)

    # volitelne
    surface_interval_min = db.Column(db.Integer)          # povrchovy interval pred timto ponorem
    deco_model = db.Column(db.String(40))                 # nazev pouziteho deko modelu
    gf_low = db.Column(db.Integer)                        # gradient faktor dolni (Buhlmann)
    gf_high = db.Column(db.Integer)                       # gradient faktor horni (Buhlmann)
    ndl_min = db.Column(db.Integer)                       # min NDL behem ponoru
    cns_max_pct = db.Column(db.Integer)                   # max CNS% dosazene behem ponoru
    otu = db.Column(db.Integer)                           # celkove OTU za ponor
    ceiling_max_m = db.Column(db.Numeric(5, 2))           # maximalni dekoStop strop v metrech
    source_meta_json = db.Column(db.JSON)                 # metadata z importu (napr Subsurface fingerprint)
    notes = db.Column(db.Text)

    # relationships, vse s cascade delete (mazanim ponoru se smaze i detail)
    license = relationship("License", back_populates="dives", lazy=True)
    device = relationship("Device", back_populates="dives", lazy=True)
    site = relationship("Site", back_populates="dives", lazy=True)
    trip = relationship("Trip", back_populates="dives", lazy=True)

    tanks = relationship("DiveTank", back_populates="dive",
                         lazy=True, cascade="all, delete-orphan")
    segments = relationship(
        "DiveSegment", back_populates="dive", lazy=True, cascade="all, delete-orphan")
    samples = relationship(
        "ProfileSample",
        back_populates="dive",
        lazy=True,
        cascade="all, delete-orphan",
        order_by="ProfileSample.t_min",   # razeni vzorku profilu chronologicky
    )
    events = relationship("DiveEvent", back_populates="dive",
                          lazy=True, cascade="all, delete-orphan")
    buddies = relationship("DiveBuddy", back_populates="dive",
                           lazy=True, cascade="all, delete-orphan")
    tags = relationship("DiveTag", back_populates="dive",
                        lazy=True, cascade="all, delete-orphan")
    attachments = relationship(
        "DiveAttachment", back_populates="dive", lazy=True, cascade="all, delete-orphan"
    )
    exposure = relationship(
        "ExposureMetrics", back_populates="dive", lazy=True, uselist=False, cascade="all, delete-orphan"
    )  # 1:1 vztah - jeden ponor ma nejvyse jeden zaznam expozice O2
    equipment = relationship(
        "DiveEquipment", back_populates="dive", lazy=True, cascade="all, delete-orphan"
    )
    media = relationship("Media", back_populates="dive", lazy=True, cascade="all, delete-orphan",
                         )

    __table_args__ = (
        CheckConstraint("duration_min IS NULL OR duration_min >= 0",
                        name="chk_duration_min_nonneg"),
        CheckConstraint("max_depth_m IS NULL OR max_depth_m >= 0",
                        name="chk_max_depth_nonneg"),
        CheckConstraint("avg_depth_m IS NULL OR avg_depth_m >= 0",
                        name="chk_avg_depth_nonneg"),
    )

    def __repr__(self):
        return f"<Dive id={self.dive_id} user={self.user_id} start={self.start_time}>"
