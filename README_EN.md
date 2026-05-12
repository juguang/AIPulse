[中文](./README.md)

# AI Pulse

Curated AI news aggregation platform — automatically crawls, classifies, tags, and recommends AI news from multiple sources.

## Features

- **Multi-source crawling** — RSS/Atom, Web (JS-rendered), HackerNews, Twitter/X, arXiv, HuggingFace Daily Papers
- **AI pipeline** — auto-classification, summarization, tagging, relevance scoring (powered by DeepSeek API)
- **Feed browsing** — category filter, keyword search, pagination
- **Dark/Light theme** — toggle for eye comfort
- **Scheduled updates** — crawl every 30 min, AI process every 15 min via APScheduler

## System Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| [Python](https://www.python.org/) | >= 3.13 | Backend runtime |
| [Node.js](https://nodejs.org/) | >= 20 | OpenCLI + frontend build |
| [pnpm](https://pnpm.io/) | latest | Frontend package manager |
| [OpenCLI](https://www.npmjs.com/package/opencli) | >= 1.7 | Web rendering, Twitter/HN sources |

## Quick Start

```bash
# 1. Configure environment
cp .env.example .env
# Edit .env, fill in DEEPSEEK_API_KEY

# 2. Install backend
uv sync

# 3. Install frontend
cd frontend && pnpm install

# 4. Install OpenCLI (required by some sources)
npm install -g opencli

# 5. Run database migrations
uv run alembic upgrade head\n\n# 6. Seed data sources (first run only)\nuv run python -m app.seed_sources
```

### Start Dev Server

```bash
# Terminal 1: Backend API (hot-reload)
uv run uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend dev server
cd frontend && pnpm dev
```

Open http://localhost:5173 to browse.

## Environment Variables

Copy `.env.example` to `.env` and configure:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite+aiosqlite://./aipulse.db` |
| `DEEPSEEK_API_KEY` | DeepSeek API key | **(required)** |
| `DEEPSEEK_BASE_URL` | DeepSeek API endpoint | `https://api.deepseek.com` |
| `DEEPSEEK_MODEL` | AI model name | `deepseek-v4-flash` |
| `CORS_ORIGINS` | Allowed frontend origins | `http://localhost:5173,http://localhost:3000` |
| `AI_PIPELINE_BATCH_SIZE` | AI processing batch size | `5` |

## Data Sources

| Source | Fetcher Type | Dependency |
|--------|-------------|------------|
| RSS/Atom feeds | `rss` | none |
| Chinese tech media (JS-rendered) | `opencli_web` | OpenCLI |
| HackerNews | `hackernews` | OpenCLI |
| Twitter/X | `twitter` | OpenCLI + browser login |
| arXiv papers | `arxiv` | none |
| HuggingFace Daily Papers | `hf_papers` | none |

## Tech Stack

- **Backend** — Python 3.13 / FastAPI / SQLAlchemy / APScheduler
- **Frontend** — React 19 / TanStack Router / Tailwind CSS 4 / Zustand
- **AI** — DeepSeek API / aiosqlite
- **Crawler** — feedparser / httpx / OpenCLI
