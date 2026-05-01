# model o exportu dat (historie o vlozeni dat UDDF, PDF, JSON, CSV)
from app.db import db


class EtlExport(db.Model):
    __tablename__ = "etl_export"

    export_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        "app_user.user_id"), nullable=False, index=True)

    format = db.Column(db.String(20), nullable=False)  # format exportovaneho souboru uddf/pdf/json/csv
    url = db.Column(db.String(300))                    # URL nebo cesta k vygenerovanemu souboru
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=db.func.now())

    def __repr__(self):
        return f"<EtlExport id={self.export_id} user={self.user_id} format={self.format}>"
