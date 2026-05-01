# aplikacni sluzby services, exportuje funkce pro snadny import
# Re-export rozsirenych statistickych funkci, dostupnost primo z app.services.
from .extended_stats_service import (
    get_user_gas_mix_stats,
    get_user_tank_stats,
    get_user_tag_stats,
    get_user_dive_event_stats,
    get_user_circuit_stats,
    get_user_license_stats,
    get_user_site_country_stats,
    get_user_site_region_stats,
    get_global_gas_mix_stats,
    get_global_tank_stats,
    get_global_tag_stats,
    get_global_dive_event_stats,
    get_global_circuit_stats,
    get_global_license_stats,
    get_global_site_country_stats,
    get_global_site_region_stats,
)
