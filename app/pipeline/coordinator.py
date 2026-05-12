"""AI Pipeline coordinator — orchestrates the full content processing pipeline.

Flow for each article:
    1. Layer 3 Title Dedup (string similarity > 0.85 threshold)
    2. Classification + Tagging (DeepSeek via router)
    3. Summarization (DeepSeek via router)
    4. Scoring + Recommendation (DeepSeek via router)
    5. Write ProcessedItem with accumulated cost tracking

Architecture:
    - Per-item sessions for error isolation (one item failure never blocks batch)
    - Pre-loads recent titles for dedup window
    - Pure functions — no FastAPI dependency, callable from scheduler or manually
"""

import json
import logging
import re
from datetime import datetime, timezone, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.config import settings
from app.database import AsyncSessionLocal
from app.llm.client import LLMClients
from app.llm.prompts import (
    CLASSIFICATION_SYSTEM,
    CLASSIFICATION_USER,
    SUMMARIZATION_SYSTEM,
    SUMMARIZATION_USER,
    SCORING_SYSTEM,
    SCORING_USER,
)
from app.llm.router import ModelRouter
from app.models.processed_item import ProcessedItem
from app.models.raw_item import RawItem
from app.pipeline.dedup import SemanticDeduplicator

logger = logging.getLogger(__name__)


def _extract_json(text: str) -> dict:
    """Extract JSON from LLM response, handling markdown code block wrapping."""
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Cannot extract JSON from response: {text[:200]}")


async def get_recent_titles(days: int = 3) -> list[str]:
    """Get titles of recently processed articles for dedup.

    Args:
        days: How many days back to look for processed articles.

    Returns:
        List of titles from recently processed articles.
    """
    async with AsyncSessionLocal() as db:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        result = await db.execute(
            select(RawItem.title)
            .join(ProcessedItem, RawItem.id == ProcessedItem.raw_item_id)
            .where(ProcessedItem.processed_at >= cutoff)
        )
        return [row[0] for row in result.all()]


async def process_single_item(
    item_id: int,
    router: ModelRouter,
    deduper: SemanticDeduplicator,
    existing_titles: list[str],
) -> str:
    """Process a single raw_item through the full AI pipeline.

    Per-item session management ensures error isolation: if this item fails,
    it does not affect other items in the batch.

    Args:
        item_id: RawItem ID to process.
        router: Initialized ModelRouter instance.
        deduper: Initialized SemanticDeduplicator instance.
        existing_titles: List of titles from previously processed articles.

    Returns:
        New status string: "processed", "duplicate", or "failed".
    """
    # --- Phase 1: Fetch and lock item ---
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(RawItem)
            .options(selectinload(RawItem.source))
            .where(RawItem.id == item_id)
        )
        item = result.scalar_one_or_none()
        if item is None:
            logger.warning("Item %d not found — skipping", item_id)
            return "failed"

        if item.status != "pending":
            logger.info(
                "Item %d status is '%s' — skipping (not pending)", item_id, item.status
            )
            return item.status

        item.status = "processing"
        await db.commit()

    source_type = item.source.type if item.source else ""
    source_name = item.source.name if item.source else ""

    try:
        # --- Phase 2: Layer 3 Title Dedup ---
        if deduper.is_duplicate(item.title, existing_titles):
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(RawItem).where(RawItem.id == item_id)
                )
                item = result.scalar_one_or_none()
                if item:
                    item.status = "duplicate"
                    await db.commit()
            logger.info("Item %d is a near-duplicate — skipped", item_id)
            return "duplicate"

        content = item.content_normalized or item.content_raw or ""

        # --- Phase 3: Classification + Tagging ---
        if source_type in ("arxiv", "hf_papers"):
            classification_user = CLASSIFICATION_USER.format(
                source_type=source_type,
                source_name=source_name,
                title=item.title,
                summary="",
                content=content[:4000],
            )
            class_result, class_cost = await router.process(
                "classification",
                system_prompt=CLASSIFICATION_SYSTEM,
                user_prompt=classification_user,
            )
            class_data = _extract_json(class_result)
            category = "研究"
            tags = class_data.get("tags", [])
        else:
            classification_user = CLASSIFICATION_USER.format(
                source_type=source_type,
                source_name=source_name,
                title=item.title,
                summary="",
                content=content[:4000],
            )
            class_result, class_cost = await router.process(
                "classification",
                system_prompt=CLASSIFICATION_SYSTEM,
                user_prompt=classification_user,
            )
            class_data = _extract_json(class_result)
            category = class_data.get("category", "行业")
            tags = class_data.get("tags", [])

        # --- Phase 4: Summarization ---
        summarization_user = SUMMARIZATION_USER.format(
            title=item.title,
            author=item.author or "未知",
            source="AI资讯",
            content=content[:6000],
        )
        summary, summary_cost = await router.process(
            "summarization",
            system_prompt=SUMMARIZATION_SYSTEM,
            user_prompt=summarization_user,
        )
        summary = summary.strip()

        # --- Phase 5: Scoring + Recommendation ---
        scoring_user = SCORING_USER.format(
            title=item.title,
            summary=summary[:2000],
            category=category,
            tags=", ".join(tags) if tags else "",
        )
        score_result, score_cost = await router.process(
            "scoring",
            system_prompt=SCORING_SYSTEM,
            user_prompt=scoring_user,
        )
        score_data = _extract_json(score_result)
        score = float(score_data.get("score", 3))
        reason = score_data.get("reason", "")

        # --- Phase 6: Write ProcessedItem with accumulated costs ---
        model_used = f"{class_cost.model}+{summary_cost.model}+{score_cost.model}"
        total_input = (
            class_cost.input_tokens
            + summary_cost.input_tokens
            + score_cost.input_tokens
        )
        total_output = (
            class_cost.output_tokens
            + summary_cost.output_tokens
            + score_cost.output_tokens
        )
        total_cost = round(
            class_cost.cost_usd + summary_cost.cost_usd + score_cost.cost_usd, 6
        )

        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(RawItem).where(RawItem.id == item_id)
            )
            item = result.scalar_one_or_none()
            if item is None:
                logger.warning(
                    "Item %d disappeared during processing — skipping write", item_id
                )
                return "failed"

            processed = ProcessedItem(
                raw_item_id=item.id,
                summary=summary,
                tags=tags,
                category=category,
                recommended_score=score,
                recommendation_reason=reason,
                llm_model_used=model_used,
                input_tokens=total_input,
                output_tokens=total_output,
                cost_usd=total_cost,
            )
            db.add(processed)
            item.status = "processed"
            await db.commit()

        logger.info(
            "Item %d processed: category=%s score=%.1f cost=$%.6f",
            item_id,
            category,
            score,
            total_cost,
        )
        return "processed"

    except Exception as exc:
        logger.error(
            "Failed to process item %d: %s", item_id, str(exc), exc_info=True
        )
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(RawItem).where(RawItem.id == item_id)
            )
            item = result.scalar_one_or_none()
            if item:
                item.status = "failed"
                item.error_message = str(exc)[:500]
                item.retry_count = (item.retry_count or 0) + 1
                await db.commit()
        return "failed"


async def process_pending_items(batch_size: Optional[int] = None) -> int:
    """Poll pending raw_items and process them through the AI pipeline.

    Main entry point for the AI content processing pipeline. Called by the
    APScheduler job or invoked manually for debugging.

    Pipeline flow per batch:
        1. Query raw_items WHERE status='pending' ORDER BY fetched_at LIMIT N
        2. Pre-load recent article titles for dedup window (3 days)
        3. For each item (per-item session, error-isolated):
            a. Title dedup check
            b. LLM classification + tagging
            c. LLM summarization
            d. LLM scoring
            e. Write ProcessedItem with cumulative cost tracking
        4. Return count of items processed

    Args:
        batch_size: Maximum items to process. Defaults to config value.

    Returns:
        Number of items processed in this batch.
    """
    if batch_size is None:
        batch_size = settings.AI_PIPELINE_BATCH_SIZE

    if not settings.DEEPSEEK_API_KEY:
        logger.warning("DEEPSEEK_API_KEY not set — AI pipeline disabled")
        return 0

    clients = LLMClients.from_settings(settings)
    router = ModelRouter(clients=clients, settings=settings)
    deduper = SemanticDeduplicator()

    # Pre-load recent titles for dedup window (3 days)
    try:
        existing_titles = await get_recent_titles(days=3)
        logger.info(
            "Loaded %d recent article titles for dedup window", len(existing_titles)
        )
    except Exception as exc:
        logger.warning("Failed to load recent titles: %s — proceeding without", exc)
        existing_titles = []

    # Poll pending items
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(RawItem)
            .where(RawItem.status == "pending")
            .where(RawItem.retry_count < settings.MAX_RETRIES)
            .order_by(RawItem.fetched_at)
            .limit(batch_size)
        )
        pending_items = result.scalars().all()

    if not pending_items:
        logger.debug("No pending items to process")
        return 0

    logger.info(
        "Processing %d pending items (batch_size=%d)", len(pending_items), batch_size
    )

    # Process each item with per-item error isolation
    titles_cache: list[str] = list(existing_titles)
    processed_count = 0

    for item in pending_items:
        status = await process_single_item(
            item_id=item.id,
            router=router,
            deduper=deduper,
            existing_titles=titles_cache,
        )

        if status == "processed":
            processed_count += 1
            titles_cache.append(item.title)

    await clients.close()

    logger.info("Batch complete: %d/%d items processed", processed_count, len(pending_items))
    return processed_count
