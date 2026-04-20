from __future__ import annotations

from ..config import SourceConfig
from .base import BaseParser
from .passion import PassionParser
from .rss import RSSParser


HTML_PARSERS = {
    "passion": PassionParser,
}


def build_parser(src: SourceConfig) -> BaseParser:
    if src.type == "rss":
        return RSSParser(src.name, src.url)
    if src.type == "html":
        key = src.parser or src.name
        cls = HTML_PARSERS.get(key)
        if not cls:
            raise ValueError(f"No HTML parser registered for '{key}' (source {src.name})")
        return cls(src.name, src.url)
    raise ValueError(f"Unknown source type: {src.type}")
