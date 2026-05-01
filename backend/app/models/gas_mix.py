# model plynove smesi, vzduch nitrox, trimix, helitrox
from app.db import db
from sqlalchemy import CheckConstraint, UniqueConstraint


class GasMix(db.Model):
    __tablename__ = "gas_mix"

    gas_mix_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("app_user.user_id"),
        nullable=False,
        index=True,
    )

    # typ smesi air/nitrox/trimix/heliox/other
    gas_type = db.Column(db.String(20), nullable=False)
    o2_percent = db.Column(db.Numeric(5, 2))             # obsah O2 v procentech (0..100)
    he_percent = db.Column(db.Numeric(5, 2))             # obsah He v procentech (0..100), 0 pro nitrox/vzduch

    active = db.Column(db.Boolean, nullable=False, server_default="true")  # soft-deaktivace smesi
    # nazev smesi, AIR, EAN32, TX18/45
    name = db.Column(db.String(40))

    __table_args__ = (
        CheckConstraint(
            "(o2_percent IS NULL OR (o2_percent >= 0 AND o2_percent <= 100))", name="chk_o2_0_100"),
        CheckConstraint(
            "(he_percent IS NULL OR (he_percent >= 0 AND he_percent <= 100))", name="chk_he_0_100"),

        # unikatnost kombinace plynu je per-uzivatel, ne globalni
        UniqueConstraint("user_id", "gas_type", "o2_percent",
                         "he_percent", name="uq_user_gas_mix"),
    )

    def __repr__(self):
        o2 = f"{float(self.o2_percent):.0f}%" if self.o2_percent is not None else "-"
        he = f"{float(self.he_percent):.0f}%" if self.he_percent is not None else "-"
        return f"<GasMix user={self.user_id} {self.gas_type} O2={o2} He={he}>"
