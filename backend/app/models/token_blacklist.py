# model seznamu zneplatnenych JWT tokenu (TokenBlacklist) po odhlaseni revokace zde a pri prihlaseni kontrola o tom ze se neshoduji
from app.db import db
from sqlalchemy.sql import func


class TokenBlacklist(db.Model):
    __tablename__ = "token_blacklist"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    jti = db.Column(db.String(36), nullable=False, unique=True, index=True)  # JWT ID unikatni identifikator tokenu
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)

    # volitelne pro pridani expiraci / typ tokenu
    # token_type = db.Column(db.String(20))  # access/refresh
    # expires_at = db.Column(db.DateTime(timezone=True))

    def __repr__(self):
        return f"<TokenBlacklist {self.jti}>"
