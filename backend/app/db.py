# umoznuje importy from app.db import db, migrate
# Samotne instance jsou definovany v extensions.py
from .extensions import db, migrate  # noqa: F401
