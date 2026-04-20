from __future__ import annotations

import logging
from datetime import datetime, timezone
from time import mktime

import feedparser
import httpx

from ..models import Article
from .base import BaseParser

log = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)
TIMEOUT = 20


class RSSParser(BaseParser):
    def fetch(self) -> list[Article]:
        try:
            resp = httpx.get(
                self.url,
                headers={"User-Agent": USER_AGENT},
                timeout=TIMEOUT,
                follow_redirects=True,
            )
            resp.raise_for_status()
        except httpx.HTTPError as e:
            log.warning("RSS fetch failed for %s: %s", self.source_name, e)
            return []

        feed = feedparser.parse(resp.content)
        articles: list[Article] = []
        for entry in feed.entries:
            url = entry.get("link", "").strip()
            title = entry.get("title", "").strip()
            if not url or not title:
                continue

            summary = entry.get("summary", "") or entry.get("description", "") or ""
            summary = _strip_html(summary).strip()

            image_url = _extract_image(entry)
            published = _parse_date(entry)

            articles.append(
                Article(
                    source=self.source_name,
                    url=url,
                    title=title,
                    summary=summary,
                    image_url=image_url,
                    published_at=published,
                )
            )
        log.info("RSS %s: %d entries", self.source_name, len(articles))
        return articles


def _extract_image(entry) -> str | None:
    for enc in entry.get("enclosures", []) or []:
        href = enc.get("href") or enc.get("url")
        typ = enc.get("type", "")
        if href and typ.startswith("image"):
            return href
    media = entry.get("media_content") or []
    if media and isinstance(media, list):
        for m in media:
            if m.get("url"):
                return m["url"]
    thumb = entry.get("media_thumbnail") or []
    if thumb and isinstance(thumb, list):
        for t in thumb:
            if t.get("url"):
                return t["url"]
    return None


def _parse_date(entry) -> datetime | None:
    t = entry.get("published_parsed") or entry.get("updated_parsed")
    if not t:
        return None
    try:
        return datetime.fromtimestamp(mktime(t), tz=timezone.utc)
    except (OverflowError, ValueError):
        return None


def _strip_html(s: str) -> str:
    from selectolax.parser import HTMLParser

    try:
        return HTMLParser(s).text(separator=" ")
    except Exception:
        return s
