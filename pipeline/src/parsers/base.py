from __future__ import annotations

from abc import ABC, abstractmethod

from ..models import Article


class BaseParser(ABC):
    def __init__(self, source_name: str, url: str):
        self.source_name = source_name
        self.url = url

    @abstractmethod
    def fetch(self) -> list[Article]:
        ...
