"""Static constants split into focused modules.
This shim re-exports names to keep existing imports working.
"""

from static_parts.ids import RISK_AREA_CHARACTERS, ALL_CHAMPIONS_IDs, TEN_ROLES_DICT
from static_parts.regions import REGIONS_TUPLE, SPECTATOR_MODE, WINDOWS_USER, TRACE_RANGE, TODAY
from static_parts.css import CropCoords, MelCSS
from static_parts.urls import URL
from static_parts.paths import PATH, Snippet, TGSMP
from static_parts.texts import TelegramStr
from static_parts.misc import MCFException, MCFTimeoutError, MCFNoConnectionError, MCFThread
from static_parts.headers import HEADERS, STATS_BASE_ITERATOR, COOKIES

__all__ = [
    # ids
    "RISK_AREA_CHARACTERS", "ALL_CHAMPIONS_IDs", "TEN_ROLES_DICT",
    # regions
    "REGIONS_TUPLE", "SPECTATOR_MODE", "WINDOWS_USER", "TRACE_RANGE", "TODAY",
    # css
    "CropCoords", "MelCSS",
    # urls
    "URL",
    # paths and snippets
    "PATH", "Snippet", "TGSMP",
    # texts
    "TelegramStr",
    # misc
    "MCFException", "MCFTimeoutError", "MCFNoConnectionError", "MCFThread",
    # headers
    "HEADERS", "STATS_BASE_ITERATOR", "COOKIES",
]

