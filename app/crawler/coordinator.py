"""Crawl orchestration with source isolation."""

import asyncio
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crawler.registry import get_fetcher, list_fetcher_types
from app.crawler.normalizer import normalize_url, compute_content_hash, ensure_timezone
from app.models.raw_item import RawItem
from app.models.source_config import SourceConfig
from app.database import AsyncSessionLocal


async def crawl_single_source(source: SourceConfig) -> dict[str, Any]:
    """Crawl a single source, return result summary."""
    result = {"source_id": source.id, "source_name": source.name, "status": "ok", "items_fetched": 0, "error": None}

    try:
        fetcher_cls = get_fetcher(source.type)
        fetcher = fetcher_cls(source)
        articles = await fetcher.fetch()
    except ValueError as e:
        result["status"] = "error"
        result["error"] = str(e)
        return result
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        return result

    inserted = 0
    async with AsyncSessionLocal() as session:
        for article in articles:
            try:
                raw = RawItem(
                    source_id=source.id,
                    guid=article["guid"],
                    title=article["title"],
                    url=normalize_url(article["url"]),
                    content_raw=article.get("content_raw"),
                    author=article.get("author"),
                    published_at=ensure_timezone(article.get("published_at")),
                    content_hash=compute_content_hash(article["title"], article["url"]),
                    raw_data=article.get("raw_data", {}),
                )
                session.add(raw)
                await session.commit()
                inserted += 1
            except Exception:
                await session.rollback()

    result["items_fetched"] = inserted
    return result


async def crawl_all_sources(session: AsyncSession) -> list[dict[str, Any]]:
    """Crawl all enabled sources concurrently."""
    result = await session.execute(
        select(SourceConfig).where(SourceConfig.enabled == True)  # noqa: E712
    )
    sources = result.scalars().all()

    tasks = [crawl_single_source(s) for s in sources]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    summaries = []
    for r in results:
        if isinstance(r, Exception):
            summaries.append({"status": "error", "error": str(r)})
        else:
            summaries.append(r)
    return summaries
