# model uzivatelskeho uctu (AppUser), pro autentizaci a autorizaci, user_id je identity v JWT
from app.db import db
from sqlalchemy import CheckConstraint


class AppUser(db.Model):
    __tablename__ = "app_user"

    # Primarni klic - identity v JWT = AppUser.user_id
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Prihlasovaci udaje
    login = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)  # hash hesla (viz utils/password.py)

    # Volitelne profilove udaje
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    phone = db.Column(db.String(40), unique=True)
    email = db.Column(db.String(120), unique=True)

    # role: 'user' (default) | 'admin'
    role = db.Column(db.String(20), nullable=False, server_default="user")
    is_active = db.Column(db.Boolean, nullable=False, server_default="true")  # soft-deaktivace uctu

    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())  # auto-aktualizace pri zmene

    __table_args__ = (
        CheckConstraint("role IN ('user','admin')", name="chk_app_user_role"),
    )

    def __repr__(self):
        return f"<AppUser {self.login} role={self.role}>"

    @property
    def is_admin(self) -> bool:
        return (self.role or "").lower() == "admin"
