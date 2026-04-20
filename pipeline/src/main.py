from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import List, Optional, Tuple

from .config import Settings, SourceConfig, load_config
from .images import download_hero_image
from .md_writer import write_article_md
from .models import Article
from .parsers.factory import build_parser
from .parsers.passion import fetch_article_body
from .rewriter import RewrittenArticle, Rewriter
from .storage import Storage


def setup_logging(level: str) -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def _fetch_body_and_image(article: Article) -> Tuple[str, str]:
    """Return (body_text, image_url). Uses passion.fetch_article_body which is generic enough."""
    body, image = fetch_article_body(article.url)
    if not image and article.image_url:
        image = article.image_url
    if not body:
        body = article.summary
    return body or "", image or ""


def collect_candidates(sources: List[SourceConfig], storage: Storage) -> List[Tuple[Article, SourceConfig]]:
    candidates: List[Tuple[Article, SourceConfig]] = []
    for src in sources:
        if not src.enabled:
            continue
        try:
            parser = build_parser(src)
            for article in parser.fetch():
                if not storage.is_seen(article):
                    candidates.append((article, src))
        except Exception as e:
            logging.exception("Parser failed for %s: %s", src.name, e)
    from datetime import datetime, timezone
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
    candidates.sort(
        key=lambda x: x[0].published_at or epoch,
        reverse=True,
    )
    return candidates


def run_once() -> int:
    settings = Settings()
    setup_logging(settings.log_level)
    log = logging.getLogger("pipeline")

    pipeline_dir = Path(__file__).resolve().parent.parent
    cfg = load_config(pipeline_dir / "config.yaml")

    storage = Storage(pipeline_dir / "data" / "news.db")

    content_dir = (pipeline_dir / settings.content_dir).resolve()
    images_dir = (pipeline_dir / settings.images_dir).resolve()

    log.info("Content dir: %s", content_dir)
    log.info("Images dir:  %s", images_dir)
    log.info("Dry run:     %s", settings.dry_run)

    candidates = collect_candidates(cfg.sources, storage)
    log.info("New candidates: %d", len(candidates))
    if not candidates:
        return 0

    limit = cfg.max_new_articles_per_cycle
    to_process = candidates[:limit]

    rewriter = None
    if not settings.dry_run:
        rewriter = Rewriter(
            api_key=settings.anthropic_api_key,
            model=settings.anthropic_model,
            base_url=settings.anthropic_base_url or None,
        )

    published = 0
    for article, src in to_process:
        log.info("Process: [%s] %s", article.source, article.title[:90])
        body_text, image_url = _fetch_body_and_image(article)
        if not body_text or len(body_text) < 120:
            log.info("Skip: too short body for %s", article.url)
            storage.mark_posted(article)
            continue

        if settings.dry_run or rewriter is None:
            log.info("DRY RUN — skipping LLM and write for %s", article.url)
            continue

        rewritten: Optional[RewrittenArticle] = rewriter.rewrite(
            article, body_text, category_hint=src.category_hint
        )
        if not rewritten:
            log.warning("Rewrite failed for %s", article.url)
            storage.mark_posted(article)
            continue

        hero_path = None
        if image_url:
            hero_path = download_hero_image(image_url, images_dir, settings.images_url_prefix)

        write_article_md(
            content_dir=content_dir,
            article=article,
            rewritten=rewritten,
            hero_image_path=hero_path,
            hero_image_alt=rewritten.title,
        )
        storage.mark_posted(article)
        published += 1

    log.info("Published %d article(s)", published)
    return published


def main() -> int:
    return 0 if run_once() >= 0 else 1


if __name__ == "__main__":
    sys.exit(main())
