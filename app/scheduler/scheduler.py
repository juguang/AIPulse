"""Crawl scheduler using APScheduler with database persistence.

Usage in FastAPI lifespan:
    from app.scheduler.scheduler import start_scheduler, stop_scheduler

    scheduler = start_scheduler()
    # ... on shutdown:
    stop_scheduler(scheduler)
"""

import logging
from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from sqlalchemy import select

from app.config import settings
from app.database import AsyncSessionLocal
from app.models.source_config import SourceConfig
from app.crawler.coordinator import crawl_all_sources
from app.pipeline.coordinator import process_pending_items

logger = logging.getLogger(__name__)

JOB_ID_CRAWL = "crawl_all_sources"
JOB_ID_PIPELINE = "ai_pipeline"


def _derive_sync_dsn(async_dsn: str) -> str:
    """Derive sync DSN from async DSN for APScheduler's SQLAlchemyJobStore."""
    return async_dsn.replace("+aiosqlite", "").replace(
        "+asyncpg", ""
    ).replace("+psycopg", "")


async def _crawl_job():
    """Job function: crawl all enabled sources."""
    logger.info("Crawl job started")
    async with AsyncSessionLocal() as session:
        results = await crawl_all_sources(session)

    ok = sum(1 for r in results if r.get("status") == "ok")
    errors = sum(1 for r in results if r.get("status") == "error")
    total_items = sum(r.get("items_fetched", 0) for r in results)
    logger.info(
        "Crawl job finished: %d sources ok, %d errors, %d new items",
        ok,
        errors,
        total_items,
    )


async def _pipeline_job():
    """Job function: process pending items through AI pipeline."""
    logger.info("AI Pipeline job started")
    try:
        count = await process_pending_items()
        logger.info("AI Pipeline job finished: %d items processed", count)
    except Exception as e:
        logger.error("AI Pipeline job failed: %s", str(e), exc_info=True)


def start_scheduler() -> AsyncIOScheduler:
    """Create and start the APScheduler instance."""
    sync_dsn = settings.SCHEDULER_DATABASE_URL or _derive_sync_dsn(settings.DATABASE_URL)

    jobstores = {
        "default": SQLAlchemyJobStore(url=sync_dsn),
    }

    scheduler = AsyncIOScheduler(jobstores=jobstores)
    interval_minutes = settings.CRAWL_INTERVAL_MINUTES

    scheduler.add_job(
        _crawl_job,
        "interval",
        minutes=interval_minutes,
        id=JOB_ID_CRAWL,
        replace_existing=True,
        misfire_grace_time=300,
    )
    pipeline_interval = settings.AI_PIPELINE_INTERVAL_MINUTES or max(1, interval_minutes // 2)
    scheduler.add_job(
        _pipeline_job,
        "interval",
        minutes=pipeline_interval,
        id=JOB_ID_PIPELINE,
        replace_existing=True,
        misfire_grace_time=300,
    )

    scheduler.start()
    logger.info("Scheduler started (interval=%d min)", interval_minutes)
    return scheduler


def stop_scheduler(scheduler: AsyncIOScheduler | None):
    """Shutdown scheduler gracefully."""
    if scheduler:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")
