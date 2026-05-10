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
| [PostgreSQL](https://www.postgresql.org/) | 16+ | Database |
| [Python](https://www.python.org/) | >= 3.13 | Backend runtime |
| [Node.js](https://nodejs.org/) | >= 20 | OpenCLI + frontend build |
| [pnpm](https://pnpm.io/) | latest | Frontend package manager |
| [OpenCLI](https://www.npmjs.com/package/opencli) | >= 1.7 | Web rendering, Twitter/HN sources |

## Quick Start

### One-command Setup

```bash
make setup
```

Creates database → installs Python deps → installs frontend deps → installs OpenCLI → runs migrations.

### Manual Setup

```bash
# 1. Configure environment
cp .env.example .env
# Edit .env, fill in DEEPSEEK_API_KEY

# 2. Create database
make db-create

# 3. Install backend
make install

# 4. Install frontend
make install-frontend

# 5. Install OpenCLI (required by some sources)
make install-opencli

# 6. Run database migrations
make migrate
```

### Start Dev Server

```bash
# Terminal 1: Backend API (hot-reload)
make dev-api

# Terminal 2: Frontend dev server
make dev-frontend
```

Open http://localhost:5173 to browse.

## Environment Variables

Copy `.env.example` to `.env` and configure:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://localhost:5432/aipulse` |
| `DEEPSEEK_API_KEY` | DeepSeek API key | **(required)** |
| `DEEPSEEK_BASE_URL` | DeepSeek API endpoint | `https://api.deepseek.com` |
| `DEEPSEEK_MODEL` | AI model name | `deepseek-chat` |
| `CORS_ORIGINS` | Allowed frontend origins | `http://localhost:5173,http://localhost:3000` |
| `AI_PIPELINE_BATCH_SIZE` | AI processing batch size | `20` |

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
- **AI** — DeepSeek API / sentence-transformers
- **Crawler** — feedparser / httpx / OpenCLI
