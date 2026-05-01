# registrace vsech API blueprintu, volana z app/api/__init__.py pri startu applikace
from .dives_routes import blp as dives_blp
from .devices_routes import blp as devices_blp
from .sites_routes import blp as sites_blp
from .gas_mixes_routes import blp as gas_mixes_blp
from .tanks_routes import blp as tanks_blp
from .license_routes import blp as licenses_blp
from .dive_tanks_routes import blp as dive_tanks_blp
from .dive_segments_routes import blp as dive_segments_blp
from .profile_samples_routes import blp as profile_samples_blp
from .dive_events_routes import blp as dive_events_blp
from .exposure_metrics_routes import blp as exposure_metrics_blp
from .buddies_routes import blp as buddies_blp
from .dive_buddies_routes import blp as dive_buddies_blp
from .tags_routes import blp as tags_blp
from .dive_tags_routes import blp as dive_tags_blp
from .media_routes import blp as media_blp
from .diver_profile_routes import blp as diver_profiles_blp
from .equipment_items_routes import blp as equipment_items_blp
from .equipment_services_routes import blp as equipment_services_blp
from .dive_equipment_routes import blp as dive_equipment_blp
from .dive_attachments_routes import blp as dive_attachments_blp
from .etl_imports_routes import blp as etl_imports_blp
from .etl_exports_routes import blp as etl_exports_blp
from .user_stats_routes import blp as user_stats_blp
from .stats_routes import blp as stats_blp
from .export_routes import blp as export_blp
from .audit_logs_routes import blp as audit_logs_blp
from .app_users_routes import blp as app_users_blp
from .token_blacklist_routes import blp as token_blacklist_blp
from .planner.calculators_routes import blp as planner_calculators_blp
from .planner.planner_routes import blp as planner_blp
from .unit_prefs_routes import blp as unit_prefs_blp
from .trips_routes import blp as trips_blp

# registruje vsechny blueprinty na Flask-Smorest Api instanci
def register_blueprints(api):
    blueprints = [
        dives_blp,
        devices_blp,
        sites_blp,
        gas_mixes_blp,
        tanks_blp,
        licenses_blp,
        dive_tanks_blp,
        dive_segments_blp,
        profile_samples_blp,
        dive_events_blp,
        exposure_metrics_blp,
        buddies_blp,
        dive_buddies_blp,
        tags_blp,
        dive_tags_blp,
        media_blp,
        diver_profiles_blp,
        equipment_items_blp,
        equipment_services_blp,
        dive_equipment_blp,
        dive_attachments_blp,
        etl_imports_blp,
        etl_exports_blp,
        user_stats_blp,
        stats_blp,
        export_blp,
        audit_logs_blp,
        app_users_blp,
        token_blacklist_blp,
        planner_calculators_blp,
        planner_blp,
        unit_prefs_blp,
        trips_blp,
    ]

    for blp in blueprints:
        api.register_blueprint(blp)
