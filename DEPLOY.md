# Развёртывание

Сайт разворачивается на **GitHub Pages**. Парсер запускается как cron-job внутри GitHub Actions. Сервер и Docker не нужны.

## 1. Установите локальные инструменты (для разработки)

```bash
# Python 3.11 (локальная 3.9 тоже подходит, но в CI — 3.11+)
# Node.js 20+ для Astro (через nvm или с сайта nodejs.org)
```

## 2. Создайте репозиторий на GitHub

Вариант A — через веб-интерфейс GitHub:
1. Зайдите на https://github.com/new
2. Имя: `womens-mag` (или любое своё)
3. **Private** или **Public** — на ваш выбор (GH Pages для Private требует платный план в Teams; в personal — бесплатно для public).
4. Создать, **не** добавляя README/gitignore (они уже есть локально).

Затем локально:

```bash
cd /Users/evgenijglozman/Projects/womens-mag
git init
git add .
git commit -m "init: Astro site scaffold + Python parser pipeline"
git branch -M main
git remote add origin https://github.com/<ВАШ_USERNAME>/womens-mag.git
git push -u origin main
```

## 3. Включите GitHub Pages

Repository → **Settings** → **Pages**:
- **Source**: GitHub Actions

## 4. Добавьте секреты и переменные

Repository → **Settings** → **Secrets and variables** → **Actions**:

**Secrets** (вкладка Secrets):
- `ANTHROPIC_API_KEY` — ключ Claude API из https://console.anthropic.com/

**Variables** (вкладка Variables):
- `SITE_URL` — финальный URL сайта.
  - Если используете дефолт GH Pages: `https://<username>.github.io/womens-mag`
  - Если прикрутили кастомный домен: `https://glyanec.ru`

## 5. Первый запуск

- Actions → **Parse, build and deploy** → **Run workflow** → main
- Первый прогон парсит ~5 источников, переписывает 6 статей через Claude, коммитит markdown, собирает Astro и деплоит на GH Pages.
- Далее запускается автоматически по cron каждые 3 часа.

## 6. Кастомный домен (опционально)

1. Купите домен (reg.ru, namecheap).
2. Добавьте CNAME-запись:
   `www  CNAME  <username>.github.io`
   и ALIAS/ANAME на apex (если провайдер поддерживает).
3. В Settings → Pages → Custom domain введите `www.glyanec.ru`, проверьте HTTPS.
4. Создайте файл `web/public/CNAME` с содержимым `www.glyanec.ru`.
5. Обновите переменную `SITE_URL` в Actions на финальный URL.

## 7. Локальная разработка

### Pipeline (парсер)

```bash
cd pipeline
python3 -m venv .venv
.venv/bin/pip install -e .
cp ../.env.example ../.env   # заполните ANTHROPIC_API_KEY
# Сухой прогон без LLM и записи файлов:
DRY_RUN=true .venv/bin/python -m src.main
# Полный прогон с записью статей:
DRY_RUN=false .venv/bin/python -m src.main
```

### Сайт (Astro)

```bash
cd web
npm install
npm run dev     # http://localhost:4321
npm run build   # сборка в web/dist
```

## Типичные проблемы

**`Woman.ru` возвращает 403 в CI** — некоторые сайты блокируют User-Agent.
Если упорно не даёт RSS — временно выключите (`enabled: false` в `config.yaml`)
или поменяйте User-Agent в `pipeline/src/parsers/rss.py`.

**Пустая главная** — пока парсер не отработал ни разу, контента нет.
Удалите `web/src/content/articles/zvezdy/example.md` после первого успешного парсинга.

**cron не срабатывает в нужное время** — GitHub задерживает cron на 10–30 мин под нагрузкой.
Это нормально для бесплатного тира.
