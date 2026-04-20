from __future__ import annotations

from typing import List, Literal, Optional

import yaml
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class SourceConfig(BaseModel):
    name: str
    type: Literal["rss", "html"]
    url: str
    parser: Optional[str] = None
    enabled: bool = True
    category_hint: Optional[str] = None


class AppConfig(BaseModel):
    poll_interval_minutes: int = 20
    max_new_articles_per_cycle: int = 6
    sources: List[SourceConfig]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    anthropic_api_key: str = ""
    anthropic_base_url: str = ""
    anthropic_model: str = "claude-opus-4-7"
    log_level: str = "INFO"
    dry_run: bool = False
    content_dir: str = "../web/src/content/articles"
    images_dir: str = "../web/public/images/articles"
    images_url_prefix: str = "/images/articles"


def load_config(path) -> AppConfig:
    with open(path, encoding="utf-8") as f:
        return AppConfig.model_validate(yaml.safe_load(f))
