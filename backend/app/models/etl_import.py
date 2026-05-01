# model o importu dat (historie importu dat)
from app.db import db


class EtlImport(db.Model):
    __tablename__ = "etl_import"

    import_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        "app_user.user_id"), nullable=False, index=True)

    # uddf/suunto_xml/sml/sde/csv format zdrojoveho souboru
    source = db.Column(db.String(40), nullable=False)
    filename = db.Column(db.String(260))                  # puvodni nazev souboru
    status = db.Column(db.String(20), nullable=False,
                       server_default="ok")               # ok/failed/partial vysledek importu
    log = db.Column(db.Text)                              # chybovy nebo informacni log importu
    checksum = db.Column(db.String(100))                  # kontrolni soucet souboru (prevence duplicit)
    raw_path = db.Column(db.String(300))                  # cesta k ulozene kopii puvodniho souboru
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=db.func.now())

    def __repr__(self):
        return f"<EtlImport id={self.import_id} user={self.user_id} source={self.source} status={self.status}>"
