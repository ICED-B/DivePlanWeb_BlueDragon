# inicializace API vrstvy, registrace vsech blueprintu na Flask-Smorest API instanci URL prefix /api/v1

def register_api(api):
    from .routes import register_blueprints
    register_blueprints(api)
