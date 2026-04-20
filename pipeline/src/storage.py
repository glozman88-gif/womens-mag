from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from .models import Article


SCHEMA = """
CREATE TABLE IF NOT EXISTS posted_articles (
    dedup_key TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    url TEXT NOT NULL,
    title TEXT NOT NULL,
    posted_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_posted_at ON posted_articles(posted_at);
"""


class Storage:
    def __init__(self, db_path: str | Path = "data/news.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._conn() as c:
            c.executescript(SCHEMA)

    @contextmanager
    def _conn(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def is_seen(self, article: Article) -> bool:
        with self._conn() as c:
            row = c.execute(
                "SELECT 1 FROM posted_articles WHERE dedup_key = ?",
                (article.dedup_key,),
            ).fetchone()
            return row is not None

    def mark_posted(self, article: Article) -> None:
        with self._conn() as c:
            c.execute(
                """
                INSERT OR IGNORE INTO posted_articles
                    (dedup_key, source, url, title, posted_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    article.dedup_key,
                    article.source,
                    article.url,
                    article.title,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )

    def last_post_time(self) -> datetime | None:
        with self._conn() as c:
            row = c.execute(
                "SELECT posted_at FROM posted_articles ORDER BY posted_at DESC LIMIT 1"
            ).fetchone()
            if not row:
                return None
            return datetime.fromisoformat(row[0])
