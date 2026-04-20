from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Article:
    source: str
    url: str
    title: str
    summary: str
    image_url: str | None
    published_at: datetime | None

    @property
    def dedup_key(self) -> str:
        return self.url.split("?")[0].rstrip("/")
