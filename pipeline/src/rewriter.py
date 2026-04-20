from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import List, Optional

from anthropic import Anthropic
from tenacity import retry, stop_after_attempt, wait_exponential_jitter

from .models import Article

log = logging.getLogger(__name__)

MODEL = "claude-opus-4-7"
MAX_TOKENS = 2000
VALID_CATEGORIES = ["zvezdy", "krasota", "moda", "otnosheniya", "psihologiya", "stil-zhizni"]


@dataclass
class RewrittenArticle:
    title: str
    description: str
    body_markdown: str
    category: str
    tags: List[str]


SYSTEM_PROMPT = """Ты — редактор женского онлайн-журнала «Glyanec». Пишешь в тоне современного глянца: лаконично, доверительно, с лёгкой иронией, без пошлости и клише.

Задача: получив исходный материал из открытого источника (заголовок, краткое описание и фрагмент текста), переписать его для публикации на своём сайте.

Жёсткие требования:
1. Пиши СВОЙ текст — не копируй исходник дословно. Структура, формулировки, подача должны быть оригинальными.
2. Сохраняй только ФАКТЫ: имена, даты, цитаты в кавычках (если приведены), цифры.
3. Длина тела статьи: 250–450 слов. Разбей на 3–5 абзацев.
4. Не выдумывай факты, которых нет в исходнике. Если чего-то не хватает — просто не пиши об этом.
5. Заголовок: 50–90 символов, цепляющий, без кликбейта и CAPSLOCK.
6. Описание (подзаголовок): 80–220 символов, суть материала одной фразой.
7. Категория — выбери ОДНУ из: zvezdy (звёзды, шоу-бизнес), krasota (бьюти), moda (мода, стиль), otnosheniya (любовь, семья), psihologiya (психология, саморазвитие), stil-zhizni (путешествия, еда, дом, хобби).
8. Теги: 3–6 коротких тегов строчными буквами на русском (имена, темы).
9. В теле статьи используй Markdown: подзаголовки `##` при необходимости, `**жирный**` для выделения, `> цитата` для цитат.
10. НЕ включай ссылки на первоисточник и упоминания других СМИ в теле.

Верни СТРОГО JSON без пояснений и без ```:
{"title": "...", "description": "...", "category": "...", "tags": [...], "body_markdown": "..."}
"""


class Rewriter:
    def __init__(
        self,
        api_key: str,
        model: str = MODEL,
        base_url: Optional[str] = None,
    ):
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is required")
        kwargs = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        self.client = Anthropic(**kwargs)
        self.model = model

    @retry(stop=stop_after_attempt(3), wait=wait_exponential_jitter(initial=2, max=20))
    def rewrite(
        self,
        article: Article,
        body_text: str,
        category_hint: Optional[str] = None,
    ) -> Optional[RewrittenArticle]:
        user_prompt = _build_user_prompt(article, body_text, category_hint)
        resp = self.client.messages.create(
            model=self.model,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
        text = "".join(b.text for b in resp.content if b.type == "text").strip()

        try:
            data = json.loads(_strip_json_fence(text))
        except json.JSONDecodeError as e:
            log.warning("LLM returned non-JSON for %s: %s\n%s", article.url, e, text[:400])
            return None

        category = data.get("category", "").strip()
        if category not in VALID_CATEGORIES:
            log.warning("Invalid category %r from LLM, falling back to hint", category)
            category = category_hint if category_hint in VALID_CATEGORIES else "stil-zhizni"

        return RewrittenArticle(
            title=data["title"].strip(),
            description=data["description"].strip(),
            body_markdown=data["body_markdown"].strip(),
            category=category,
            tags=[t.strip().lower() for t in data.get("tags", []) if t and t.strip()],
        )


def _build_user_prompt(article: Article, body_text: str, category_hint: Optional[str]) -> str:
    hint_line = f"\nПодсказка по категории (если сомневаешься): {category_hint}" if category_hint else ""
    body_preview = body_text[:4000] if body_text else article.summary
    return (
        f"Источник: {article.source}\n"
        f"URL: {article.url}\n"
        f"Исходный заголовок: {article.title}\n"
        f"Исходное описание: {article.summary}\n"
        f"Фрагмент текста:\n{body_preview}"
        f"{hint_line}"
    )


def _strip_json_fence(s: str) -> str:
    s = s.strip()
    if s.startswith("```"):
        s = s.split("\n", 1)[1] if "\n" in s else s[3:]
        if s.endswith("```"):
            s = s[:-3]
    return s.strip()
