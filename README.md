[English](./README_EN.md)

# AI Pulse

AI 资讯自动抓取、AI 分类打标签、个性化推荐的信息流聚合平台。

## 功能特性

- **多源抓取** — RSS/Atom、Web（JS 渲染）、HackerNews、Twitter/X、arXiv、HuggingFace Daily Papers
- **AI 处理** — 自动分类、摘要生成、标签提取、推荐评分（基于 DeepSeek API）
- **信息流浏览** — 按分类筛选、关键词搜索、分页浏览
- **深色/浅色主题** — 支持切换，保护视力
- **定时更新** — APScheduler 每 30 分钟自动抓取，每 15 分钟 AI 处理

## 系统依赖

| 依赖 | 版本要求 | 用途 |
|------|---------|------|
| [PostgreSQL](https://www.postgresql.org/) | 16+ | 数据库存储 |
| [Python](https://www.python.org/) | >= 3.13 | 后端运行环境 |
| [Node.js](https://nodejs.org/) | >= 20 | OpenCLI 工具 + 前端构建 |
| [pnpm](https://pnpm.io/) | 最新版 | 前端包管理 |
| [OpenCLI](https://www.npmjs.com/package/opencli) | >= 1.7 | Web 渲染抓取、Twitter/HN 数据源 |

## 快速开始

```bash
# 1. 配置环境变量
cp .env.example .env
# 编辑 .env，填入 DEEPSEEK_API_KEY

# 2. 创建 PostgreSQL 数据库
createdb aipulse

# 3. 安装后端依赖
uv sync

# 4. 安装前端依赖
cd frontend && pnpm install

# 5. 安装 OpenCLI（部分数据源需要）
npm install -g opencli

# 6. 运行数据库迁移
uv run alembic upgrade head
```

### 启动开发服务

```bash
# 终端 1：启动后端 API（热重载）
uv run uvicorn app.main:app --reload --port 8000

# 终端 2：启动前端开发服务器
cd frontend && pnpm dev
```

打开 http://localhost:5173 即可浏览。

## 环境变量

复制 `.env.example` 到 `.env` 并配置：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DATABASE_URL` | PostgreSQL 连接串 | `postgresql+asyncpg://localhost:5432/aipulse` |
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | （必填） |
| `DEEPSEEK_BASE_URL` | DeepSeek API 地址 | `https://api.deepseek.com` |
| `DEEPSEEK_MODEL` | AI 模型 | `deepseek-v4-flash` |
| `CORS_ORIGINS` | 允许的前端地址 | `http://localhost:5173,http://localhost:3000` |
| `AI_PIPELINE_BATCH_SIZE` | AI 处理批大小 | `5` |

## 数据源说明

| 数据源 | 类型 | 依赖 |
|--------|------|------|
| RSS/Atom 订阅源 | `rss` | 无额外依赖 |
| 中文科技媒体（JS 渲染） | `opencli_web` | OpenCLI |
| HackerNews | `hackernews` | OpenCLI |
| Twitter/X | `twitter` | OpenCLI + 浏览器登录 |
| arXiv 论文 | `arxiv` | 无额外依赖 |
| HuggingFace 每日论文 | `hf_papers` | 无额外依赖 |

## 技术栈

- **后端** — Python 3.13 / FastAPI / SQLAlchemy / APScheduler
- **前端** — React 19 / TanStack Router / Tailwind CSS 4 / Zustand
- **AI** — DeepSeek API / sentence-transformers
- **抓取** — feedparser / httpx / OpenCLI
