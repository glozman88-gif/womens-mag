from __future__ import annotations

import logging
import re
from urllib.parse import urljoin

import httpx
from selectolax.parser import HTMLParser

from ..models import Article
from .base import BaseParser

log = logging.getLogger(__name__)

USER_AGENT = "Mozilla/5.0 (compatible; NewsMaxBot/0.1)"
TIMEOUT = 20
MAX_ARTICLES_PER_RUN = 20

ARTICLE_PATH_RE = re.compile(
    r"^/(news/[a-z0-9\-]+|tolko-zvezdy|lyudi-takie|istorii|krasota|moda|otnosheniya)/[a-z0-9\-]+\.htm$"
)


class PassionParser(BaseParser):
    def fetch(self) -> list[Article]:
        with httpx.Client(
            headers={"User-Agent": USER_AGENT},
            timeout=TIMEOUT,
            follow_redirects=True,
        ) as client:
            try:
                resp = client.get(self.url)
                resp.raise_for_status()
            except httpx.HTTPError as e:
                log.warning("Passion homepage fetch failed: %s", e)
                return []

            doc = HTMLParser(resp.text)
            seen_paths: set[str] = set()
            candidates: list[tuple[str, str]] = []

            for a in doc.css("a[href]"):
                href = (a.attributes.get("href") or "").strip()
                if not ARTICLE_PATH_RE.match(href) or href in seen_paths:
                    continue
                title = a.text(strip=True)
                title = re.sub(r"^\d+", "", title).strip()
                if len(title) < 20:
                    continue
                seen_paths.add(href)
                candidates.append((href, title))
                if len(candidates) >= MAX_ARTICLES_PER_RUN:
                    break

            articles: list[Article] = []
            for href, title in candidates:
                full_url = urljoin(self.url, href)
                articles.append(
                    Article(
                        source=self.source_name,
                        url=full_url,
                        title=title,
                        summary="",
                        image_url=None,
                        published_at=None,
                    )
                )

        log.info("Passion: %d candidate articles", len(articles))
        return articles


def fetch_article_body(url: str) -> tuple[str, str | None]:
    """Fetch full article body + hero image for rewriter. Returns (text, image_url)."""
    try:
        resp = httpx.get(
            url,
            headers={"User-Agent": USER_AGENT},
            timeout=TIMEOUT,
            follow_redirects=True,
        )
        resp.raise_for_status()
    except httpx.HTTPError as e:
        log.warning("Article body fetch failed for %s: %s", url, e)
        return "", None

    doc = HTMLParser(resp.text)
    image = _meta(doc, "og:image")
    description = _meta(doc, "og:description") or _meta(doc, "description", attr="name")

    paragraphs: list[str] = []
    for p in doc.css("article p, .article__body p, .content p, main p"):
        text = p.text(strip=True)
        if len(text) > 40:
            paragraphs.append(text)

    body = "\n\n".join(paragraphs[:10]) if paragraphs else description or ""
    return body, image


def _meta(doc: HTMLParser, key: str, attr: str = "property") -> str | None:
    node = doc.css_first(f'meta[{attr}="{key}"]')
    if node:
        return node.attributes.get("content")
    return None
