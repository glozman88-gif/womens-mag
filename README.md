# Womens Mag (working name)

Онлайн-журнал о моде, красоте, звёздах и отношениях. Контент собирается парсером с открытых источников, переписывается через Claude API и публикуется как статический сайт.

## Архитектура

```
womens-mag/
├── pipeline/            Python-парсер + LLM-рерайт
│   ├── src/
│   │   ├── parsers/     RSS + HTML-парсеры
│   │   ├── config.py
│   │   ├── storage.py   SQLite для дедупа
│   │   ├── rewriter.py  Claude API
│   │   ├── md_writer.py markdown + frontmatter
│   │   └── main.py
│   └── config.yaml      список источников
├── web/                 Astro SSG + Tailwind
│   ├── src/
│   │   ├── content/articles/    ← сюда пишет пайплайн
│   │   ├── layouts/
│   │   ├── components/
│   │   └── pages/
│   └── public/
├── content/images/      рехостинг картинок (коммитятся в репо)
└── .github/workflows/
    └── build.yml        cron парсер → коммит → deploy
```

## Развёртывание

MVP: GitHub Actions + GitHub Pages (бесплатно).
Масштабирование: Vercel / Cloudflare Pages / собственный VPS.

## Требования для локальной разработки

- Python 3.11+
- Node.js 20+
- `ANTHROPIC_API_KEY` в `.env`
