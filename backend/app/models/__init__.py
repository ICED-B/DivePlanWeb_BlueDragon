# centralni registrace vsech SQLAlchemy medelu aplikace
# Ujisti se, ze tahle __init__ se importuje v Alembic env.py (target_metadata)
# nebo v app/__init__.py pri inicializaci aplikace.

from .license import License
from .device import Device
from .site import Site
from .gas_mix import GasMix
from .tank import Tank
from .dive import Dive
from .trip import Trip
from .dive_tank import DiveTank
from .dive_segment import DiveSegment
from .profile_sample import ProfileSample
from .dive_event import DiveEvent
from .exposure_metrics import ExposureMetrics
from .buddy import Buddy
from .dive_buddy import DiveBuddy
from .tag import Tag
from .dive_tag import DiveTag
from .media import Media
from .diver_profile import DiverProfile
from .equipment_item import EquipmentItem
from .equipment_service import EquipmentService
from .dive_equipment import DiveEquipment
from .dive_attachment import DiveAttachment
from .etl_import import EtlImport
from .etl_export import EtlExport
from .user_stats import UserStats
from .audit_log import AuditLog
from .app_user import AppUser
from .token_blacklist import TokenBlacklist
from .unit_prefs import UnitPrefs  # noqa: F401

__all__ = [
    "License", "Device", "Site", "GasMix", "Tank", "Dive",
    "Trip", "DiveTank", "DiveSegment", "ProfileSample", "DiveEvent", "ExposureMetrics",
    "Buddy", "DiveBuddy", "Tag", "DiveTag", "Media",
    "DiverProfile", "EquipmentItem", "EquipmentService", "DiveEquipment", "DiveAttachment",
    "EtlImport", "EtlExport", "UserStats", "AuditLog",
    "AppUser", "TokenBlacklist", "UnitPrefs",
]
