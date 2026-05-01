# Flask rozsireni a inicializace
# spojeno v init_extensions()
from __future__ import annotations

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_smorest import Api
from flask_marshmallow import Marshmallow

# Globalni instance pro pouziti napric aplikaci
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()
ma = Marshmallow()
api = Api()
# Limiter bez defaultu - nastavime je az v init_extensions podle app.config
limiter = Limiter(key_func=get_remote_address, default_limits=[])


def init_extensions(app):
    # Rozsireni svazany s flask app
    # ocekavane klice v app.config: CORS_ORIGINS, RATELIMIT_DEFAULT, RATELIMIT_STORAGE_URI
    
    # SQLAlchemy + Migrate
    db.init_app(app)
    migrate.init_app(app, db)

    # Marshmallow + Smorest (OpenAPI/Swagger)
    ma.init_app(app)
    api.init_app(app)

    # JWT - claims a blacklist
    jwt.init_app(app)

    @jwt.additional_claims_loader
    def add_claims(identity) -> dict:
        # Prida custom claims do JWT tokenu.
        # Claim 'role' se nacita z databaze dle identity (user_id).
        # Claim 'fresh' je vychozi False - nastavuje se pri vydani tokenu.
        claims = {"role": "user", "fresh": False}
        try:
            # Lazy import kvuli cyklickym zavislostem
            from app.models.app_user import AppUser  # type: ignore
            user_id = int(identity)
            user = db.session.get(AppUser, user_id)
            if user and getattr(user, "role", None):
                claims["role"] = user.role
        except Exception:
            pass
        return claims

    @jwt.token_in_blocklist_loader
    def is_token_revoked(jwt_headers, jwt_payload) -> bool:
        # blacklist check vraci True, pokud byl token revokovan jti je v TokenBlacklist
        # Fail-closed pri chybe DB token zamitne
        try:
            from app.models.token_blacklist import TokenBlacklist  # type: ignore

            jti = jwt_payload.get("jti")
            if not jti:
                return True
            return db.session.query(TokenBlacklist.id).filter_by(jti=jti).first() is not None
        except Exception:
            # Fail-closed v pripade chyby raději token zamitnout
            return True

    # CORS_ORIGINS z configu
    # None prazdny retezec -> vychozi pro dev ("http://localhost:5173")
    # (str -> rozdelime na list)    list[str] pouzijeme primo
    origins_cfg = app.config.get("CORS_ORIGINS")

    if origins_cfg is None or origins_cfg == "":
        origins = ["http://localhost:5173"]
    elif isinstance(origins_cfg, str):
        origins = [o.strip() for o in origins_cfg.split(",") if o.strip()]
    else:
        origins = list(origins_cfg)

    # CORS je omezen pouze na /api/* cesty
    resources = {r"/api/*": {"origins": origins}}

    cors.init_app(
        app,
        resources=resources,
        supports_credentials=True,
        allow_headers=["Authorization", "Content-Type"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        max_age=600,
    )

    # Rate Limiter
    default_limit = app.config.get("RATELIMIT_DEFAULT", "200 per minute")
    storage_uri = app.config.get("RATELIMIT_STORAGE_URI")

    limiter.default_limits = [default_limit] if default_limit else []
    if storage_uri:
        # Flask-Limiter 3.x: storage se konfiguruje pres konstruktor, workaround pro dynamicke nastaveni
        limiter._storage_uri = storage_uri
    limiter.init_app(app)
