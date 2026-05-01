# Inicializuje rozsireni, registruje blueprinty a zajisteni chyb
from __future__ import annotations

import os
from flask import Flask, jsonify

from .config import config_by_name
from .extensions import db, migrate, jwt, cors, limiter, api as smorest_api, ma, init_extensions


def create_app(config_name: str | None = None, config_override: type | None = None) -> Flask:
    # Vytvari a konfiguruje Flask aplikaci
    # param config_name (development/testing/production/default), config_override pro testovani
    if config_name is None:
        config_name = os.getenv("FLASK_CONFIG", "default")

    app = Flask(__name__)

    # Konfigurace aplikace bud pres override, nebo podle jmena
    if config_override:
        app.config.from_object(config_override)
    else:
        app.config.from_object(config_by_name[config_name])

    # Inicializace rozšíření (DB, MA, API/Swagger, JWT, CORS, Limiter, Migrate)
    init_extensions(app)

    # Dulezite pro Alembic autogenerate zaregistruje vsechny modely do db.metadata
    from . import models  # noqa: F401

    # Chybové handlery (JSON odpovědi)

    @app.errorhandler(422)
    def handle_unprocessable_entity(err):
        # Marshmallow validacni chyby na JSON odpoved
        messages = getattr(err, "data", {}).get(
            "messages", ["Unprocessable Entity"])
        return jsonify({"message": "Validation error", "errors": messages}), 422

    @app.errorhandler(429)
    def handle_rate_limit(err):
        return jsonify({"message": "Too many requests"}), 429

    @app.errorhandler(500)
    def handle_server_error(err):
        return jsonify({"message": "Internal server error"}), 500

    # Registrace Blueprintů

    # Registrace vsech CRUD API blueprintu v (api/routes/__init__.py)
    try:
        from .api import register_api
        register_api(smorest_api)
    except Exception as e:
        app.logger.warning("API v1 blueprint nebyl registrován: %s", e)

    # Auth blueprint (prihlaseni, registrace, JWT refresh, odhlaseni)
    try:
        from .auth import auth_blp
        smorest_api.register_blueprint(auth_blp)
    except Exception as e:
        app.logger.info("Auth blueprint zatím neregistrován: %s", e)

    # Shell context (flask shell)
    @app.shell_context_processor
    def make_shell_context():
        # Zpristupni db a AppUser ve Flask shellu bez nutnosti importu
        try:
            from .models.app_user import AppUser
        except Exception:
            AppUser = None
        return {"db": db, "AppUser": AppUser}

    # Testovaci route pro overeni, ze server bezi
    @app.get("/hello")
    def hello():
        return "Hello, WebDivePlanner backend is running!"

    # Health check endpoint pro Azure App Service a monitoring
    @app.get("/api/v1/health")
    def health():
        return jsonify({"status": "ok"}), 200

    return app
