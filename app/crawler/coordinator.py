"""Crawl orchestration with source isolation and health tracking."""

import asyncio
from datetime import datetime, timezone, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crawler.registry import get_fetcher
from app.crawler.normalizer import normalize_url, compute_content_hash, ensure_timezone
from app.models.raw_item import RawItem
from app.models.source_config import SourceConfig
from app.database import AsyncSessionLocal
from app.config import settings


async def _update_source_health(source_id: int, success: bool, error_msg: str | None = None):
    """Update source health metrics after a crawl attempt."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(SourceConfig).where(SourceConfig.id == source_id)
        )
        source = result.scalar_one_or_none()
        if source is None:
            return

        source.last_crawled_at = datetime.now(timezone.utc)

        if success:
            source.consecutive_failures = 0
            source.last_error = None
            source.health_score = min(1.0, (source.health_score or 1.0) + 0.1)
        else:
            source.consecutive_failures = (source.consecutive_failures or 0) + 1
            source.last_error = (error_msg or "Unknown error")[:500]
            # Exponential backoff: health decreases with consecutive failures
            source.health_score = max(0.0, (source.health_score or 1.0) - 0.2 * source.consecutive_failures)

        await session.commit()


async def crawl_single_source(source: SourceConfig) -> dict[str, Any]:
    """Crawl a single source, return result summary.

    Updates source health metrics on success/failure.
    Sources with health_score <= 0 are skipped (auto-deactivated).
    """
    result = {"source_id": source.id, "source_name": source.name, "status": "ok", "items_fetched": 0, "error": None}

    # Skip auto-deactivated sources
    if (source.health_score or 1.0) <= 0:
        result["status"] = "skipped"
        result["error"] = "Source auto-deactivated (health_score <= 0)"
        return result

    # Fetch with exponential backoff check
    backoff = (source.consecutive_failures or 0) * 10
    if backoff > 0:
        await asyncio.sleep(min(backoff, 60))  # Max 60s delay

    try:
        fetcher_cls = get_fetcher(source.type)
        fetcher = fetcher_cls(source)
        articles = await fetcher.fetch()
    except ValueError as e:
        await _update_source_health(source.id, success=False, error_msg=str(e))
        result["status"] = "error"
        result["error"] = str(e)
        return result
    except Exception as e:
        await _update_source_health(source.id, success=False, error_msg=str(e))
        result["status"] = "error"
        result["error"] = str(e)
        return result

    inserted = 0
    max_age = datetime.now(timezone.utc) - timedelta(days=settings.CRAWL_MAX_AGE_DAYS)

    async with AsyncSessionLocal() as session:
        for article in articles:
            pub_at = ensure_timezone(article.get("published_at"))
            if pub_at and pub_at < max_age:
                continue
            try:
                raw = RawItem(
                    source_id=source.id,
                    guid=article["guid"],
                    title=article["title"],
                    source_url=normalize_url(article["url"]),
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

    await _update_source_health(source.id, success=True)
    result["items_fetched"] = inserted
    return result


async def crawl_all_sources(session: AsyncSession) -> list[dict[str, Any]]:
    """Crawl all active sources concurrently."""
    result = await session.execute(
        select(SourceConfig).where(SourceConfig.active == True)  # noqa: E712
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
