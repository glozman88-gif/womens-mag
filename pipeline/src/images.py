from __future__ import annotations

import hashlib
import logging
import mimetypes
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import httpx

log = logging.getLogger(__name__)

USER_AGENT = "Mozilla/5.0 (compatible; NewsMaxBot/0.1)"
TIMEOUT = 20
MAX_BYTES = 6 * 1024 * 1024
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}


def download_hero_image(url: str, target_dir: Path, url_prefix: str) -> Optional[str]:
    """Download image, store under target_dir, return public URL path."""
    if not url:
        return None
    try:
        with httpx.Client(
            headers={"User-Agent": USER_AGENT},
            timeout=TIMEOUT,
            follow_redirects=True,
        ) as c:
            r = c.get(url)
            r.raise_for_status()
    except httpx.HTTPError as e:
        log.warning("Image fetch failed: %s (%s)", url, e)
        return None

    content_type = (r.headers.get("content-type") or "").split(";")[0].strip()
    if content_type not in ALLOWED_CONTENT_TYPES:
        log.info("Skip non-image content type %s for %s", content_type, url)
        return None

    if len(r.content) > MAX_BYTES:
        log.info("Image too large (%d bytes): %s", len(r.content), url)
        return None

    ext = mimetypes.guess_extension(content_type) or Path(urlparse(url).path).suffix or ".jpg"
    if ext == ".jpe":
        ext = ".jpg"

    h = hashlib.sha1(r.content).hexdigest()[:16]
    filename = f"{h}{ext}"

    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / filename
    if not path.exists():
        path.write_bytes(r.content)

    return f"{url_prefix.rstrip('/')}/{filename}"
