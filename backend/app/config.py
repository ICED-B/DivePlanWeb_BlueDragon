# Conf Flask aplikace, definuje zakladni a odvozene tridy pro (def/test/prod)
import os
from datetime import timedelta
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
# .env soubor ocekavame na koreni projektu (backend/../../.env)
load_dotenv(os.path.join(basedir, "../../.env"))


def _csv_env(name, default=""):
    # promenne prostredi cte jako CSV seznam
    raw = os.environ.get(name, default)
    if not raw:
        return []
    return [x.strip() for x in raw.split(",") if x.strip()]


class Config:
    # konfigurace pro rezimy
    # Flask / bezpecnost
    SECRET_KEY = os.environ.get("SECRET_KEY") or "vychozi_slabý_klíč_pro_vývoj"  # DEV ONLY

    # SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # OpenAPI / Swagger (Flask-Smorest)
    API_TITLE = "WebDivePlanner API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.3"
    OPENAPI_URL_PREFIX = "/api/docs"
    OPENAPI_SWAGGER_UI_PATH = "/swagger"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    # Globalni bezpecnostni schema pro Swagger UI - Bearer JWT token
    API_SPEC_OPTIONS = {
        "security": [{"bearerAuth": []}],
        "components": {
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                }
            }
        },
    }

    # JWT (Flask-JWT-Extended)
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or SECRET_KEY
    JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"
    # platnost access a refresh tokenu
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        minutes=int(os.environ.get("JWT_ACCESS_MINUTES", "15"))
    )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        days=int(os.environ.get("JWT_REFRESH_DAYS", "30"))
    )

    # CORS CSV seznam povolenych, napr. "http://localhost:5173,https://app.example.com"
    CORS_ORIGINS = _csv_env("CORS_ORIGINS", "http://localhost:5173")

    # Rate limiting
    RATELIMIT_DEFAULT = os.environ.get("RATELIMIT_DEFAULT", "200 per minute")
    RATELIMIT_AUTH = os.environ.get("RATELIMIT_AUTH", "10 per minute")
    # Volitelne Redis URI pro sdileny rate limit ve viceprocesorovem prostredi
    RATELIMIT_STORAGE_URI = os.environ.get("RATELIMIT_STORAGE_URI")  # napr. "redis://:pwd@host:6379/0"

    # Uploady / soubory
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH_MB", "10")) * 1024 * 1024  # 10 MB default
    UPLOAD_ALLOWED_EXTENSIONS = _csv_env(
        "UPLOAD_ALLOWED_EXTENSIONS",
        "jpg,jpeg,png,webp,pdf,uddf,xml,sml,sde,csv,json",
    )

    # V produkci nastavovat HSTS a HTTPS pres reverse proxy
    PREFERRED_URL_SCHEME = "https"


class DevelopmentConfig(Config):
    # konfigurace pro lokalni vyvoj
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL")
        or "postgresql+psycopg://user:password@localhost/dev_db"
    )
    SQLALCHEMY_ECHO = True  # vypisuje vsechny SQL dotazy do konzole


class TestingConfig(Config):
    # konfigurace pro automatizovane testy
    TESTING = True
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("TEST_DATABASE_URL") or "sqlite:///:memory:"
    )
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    # konfigurace pro produkcni nasazeni, DATABASE_URL musi byt nastaveno v prostredi
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")  # MUSI byt nastaveno v prostredi
    # V produkci doplnit: SECURE_COOKIES, HSTS, strukturovane logovani atd.


# Mapovani nazvu konfigurace na tridu - pouziva se v create_app()
config_by_name = dict(
    development=DevelopmentConfig,
    testing=TestingConfig,
    production=ProductionConfig,
    default=DevelopmentConfig,
)


def get_secret_key():
    # vrati SECRET_KEY z prostredi. V pripade chybejici hodnoty vypise varovani (pouze pro DEV)
    key = os.environ.get("SECRET_KEY")
    if not key:
        print("VAROVÁNÍ: SECRET_KEY není nastaven v .env souboru!")
        key = "vychozi_slabý_klíč_pro_vývoj_oprav_mne"
    return key
