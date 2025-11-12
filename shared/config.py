"""Lightweight config accessor with in-memory cache.

Separates read-only configuration (uparams) from runtime logic.
"""

from __future__ import annotations

import threading
from typing import Any, Dict
from static import PATH
from shared.storage import SafeJson


class Config:
    _lock = threading.Lock()
    _cache: Dict[str, Any] | None = None

    @classmethod
    def _load(cls) -> Dict[str, Any]:
        # Lazy load and cache uparams.json
        if cls._cache is None:
            with cls._lock:
                if cls._cache is None:
                    cls._cache = SafeJson.load(PATH.UPARAMS)
        return cls._cache  # type: ignore[return-value]

    @classmethod
    def get(cls, key: str, default: Any | None = None) -> Any:
        data = cls._load()
        return data.get(key, default)

    @classmethod
    def proxies(cls) -> Any:
        return cls.get("PROXIES")

    @classmethod
    def riot_api_key(cls) -> str:
        return cls.get("RIOT_API")

    @classmethod
    def tg_token(cls) -> str:
        return cls.get("BOT_TOKEN")

    @classmethod
    def tg_chat_pub(cls) -> int:
        return cls.get("CHAT_ID_PUB")

    @classmethod
    def tg_chat_pr(cls) -> int:
        return cls.get("CHAT_ID_PR")

