"""Seed initial source configurations for AI Pulse content pipeline.

Usage: uv run python -m app.seed_sources
"""

import asyncio
from app.database import AsyncSessionLocal
from app.models.source_config import SourceConfig
from sqlalchemy import select


SOURCES = [
    # RSS/Atom feeds
    {"name": "OpenAI Blog", "type": "rss", "url": "https://openai.com/blog/rss.xml", "enabled": True},
    {"name": "Anthropic Blog", "type": "rss", "url": "https://www.anthropic.com/rss.xml", "enabled": True},
    {"name": "Google AI Blog", "type": "rss", "url": "https://blog.google/technology/ai/rss/", "enabled": True},
    {"name": "IT之家 AI", "type": "rss", "url": "https://rss.ithome.com/ai.xml", "enabled": True},
    {"name": "Hugging Face Blog", "type": "rss", "url": "https://huggingface.co/blog/feed.xml", "enabled": True},
    {"name": "Arxiv AI (RSS)", "type": "rss", "url": "https://rss.arxiv.org/rss/cs.AI", "enabled": True},

    # OpenCLI sources
    {"name": "HackerNews", "type": "hackernews", "url": "", "enabled": True, "config": {"limit": 30}},
    {"name": "Arxiv AI (OpenCLI)", "type": "arxiv", "url": "", "enabled": True, "config": {"category": "cs.AI", "limit": 30}},

    # Social media
    {"name": "Twitter/X AI", "type": "twitter", "url": "", "enabled": True,
     "config": {"query": "AI", "limit": 20, "accounts": []}},

    # HuggingFace
    {"name": "HuggingFace Papers", "type": "huggingface", "url": "", "enabled": True, "config": {"limit": 20}},
]


async def seed():
    async with AsyncSessionLocal() as session:
        # Check if already seeded
        result = await session.execute(select(SourceConfig).limit(1))
        if result.scalar_one_or_none():
            print("Sources already seeded, skipping.")
            return

        for s in SOURCES:
            source = SourceConfig(
                name=s["name"],
                type=s["type"],
                url=s.get("url", ""),
                enabled=s["enabled"],
                config=s.get("config", {}),
            )
            session.add(source)

        await session.commit()
        print(f"Seeded {len(SOURCES)} sources.")


if __name__ == "__main__":
    asyncio.run(seed())
