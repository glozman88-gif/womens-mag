from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .models import Article
from .rewriter import RewrittenArticle

log = logging.getLogger(__name__)


def slugify(text: str, max_len: int = 80) -> str:
    """Simple slug: Cyrillic-aware transliteration + cleanup."""
    s = _translit(text).lower()
    s = re.sub(r"[^a-z0-9\s\-]+", "", s)
    s = re.sub(r"[\s\-]+", "-", s).strip("-")
    return s[:max_len].rstrip("-") or "article"


_TRANSLIT_MAP = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e", "ж": "zh",
    "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m", "н": "n", "о": "o",
    "п": "p", "р": "r", "с": "s", "т": "t", "у": "u", "ф": "f", "х": "h", "ц": "c",
    "ч": "ch", "ш": "sh", "щ": "sch", "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu",
    "я": "ya",
}


def _translit(text: str) -> str:
    out = []
    for ch in text:
        lower = ch.lower()
        rep = _TRANSLIT_MAP.get(lower, ch)
        if ch.isupper() and rep:
            rep = rep[0].upper() + rep[1:]
        out.append(rep)
    return "".join(out)


def write_article_md(
    content_dir: Path,
    article: Article,
    rewritten: RewrittenArticle,
    hero_image_path: Optional[str],
    hero_image_alt: Optional[str],
) -> Path:
    slug = slugify(rewritten.title)
    content_dir.mkdir(parents=True, exist_ok=True)

    path = content_dir / f"{slug}.md"
    counter = 2
    while path.exists():
        path = content_dir / f"{slug}-{counter}.md"
        counter += 1

    published = article.published_at or datetime.now(timezone.utc)

    frontmatter_lines = [
        "---",
        f"title: {_yaml_str(rewritten.title)}",
        f"description: {_yaml_str(rewritten.description)}",
        f'category: "{rewritten.category}"',
        f"tags: [{', '.join(_yaml_str(t) for t in rewritten.tags)}]",
    ]
    if hero_image_path:
        frontmatter_lines.append(f"heroImage: {_yaml_str(hero_image_path)}")
    if hero_image_alt:
        frontmatter_lines.append(f"heroImageAlt: {_yaml_str(hero_image_alt)}")
    frontmatter_lines += [
        f"publishedAt: {published.replace(microsecond=0).isoformat()}",
        f"sourceUrl: {_yaml_str(article.url)}",
        f"sourceName: {_yaml_str(article.source)}",
        'author: "Редакция Glyanec"',
        "draft: false",
        "---",
        "",
    ]

    body = rewritten.body_markdown.strip() + "\n"
    path.write_text("\n".join(frontmatter_lines) + body, encoding="utf-8")
    log.info("Wrote markdown: %s", path)
    return path


def _yaml_str(s: str) -> str:
    """Safe-quote a string for YAML frontmatter."""
    s = s.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{s}"'
