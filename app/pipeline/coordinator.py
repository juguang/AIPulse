"""AI Pipeline coordinator — orchestrates the full content processing pipeline.

Flow for each article:
    1. Layer 3 Semantic Dedup (cosine similarity > 0.75 threshold)
    2. Classification + Tagging (DeepSeek via router)
    3. Summarization (DeepSeek via router)
    4. Scoring + Recommendation (DeepSeek via router)
    5. Write ProcessedItem with accumulated cost tracking

Architecture:
    - Per-item sessions for error isolation (one item failure never blocks batch)
    - Pre-loads recent embeddings for semantic dedup window
    - Pure functions — no FastAPI dependency, callable from scheduler or manually
"""

import json
import logging
import re
from datetime import datetime, timezone, timedelta
from typing import Optional

import numpy as np
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
    """Extract JSON from LLM response, handling markdown code block wrapping.

    LLMs sometimes wrap JSON output in ```json ... ``` blocks. This helper
    tries direct json.loads() first, then falls back to extracting from
    markdown code fences.
    """
    text = text.strip()
    # Try direct parse first (most common for structured prompts)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try extracting from ```json ... ``` block
    match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Cannot extract JSON from response: {text[:200]}")


async def get_recent_embeddings(days: int = 3) -> np.ndarray:
    """Get sentence embeddings for titles of recently processed articles.

    Queries ProcessedItem joined with RawItem for the last N days,
    extracts titles, and encodes them via SemanticDeduplicator.

    Args:
        days: How many days back to look for processed articles.

    Returns:
        (N, 384) numpy array of normalized embeddings, or empty array.
    """
    deduper = SemanticDeduplicator()
    async with AsyncSessionLocal() as db:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        result = await db.execute(
            select(RawItem.title)
            .join(ProcessedItem, RawItem.id == ProcessedItem.raw_item_id)
            .where(ProcessedItem.processed_at >= cutoff)
        )
        titles = [row[0] for row in result.all()]

    if not titles:
        return np.array([])

    return deduper.encode(titles)


async def process_single_item(
    item_id: int,
    router: ModelRouter,
    deduper: SemanticDeduplicator,
    existing_embeddings: np.ndarray,
) -> str:
    """Process a single raw_item through the full AI pipeline.

    Per-item session management ensures error isolation: if this item fails,
    it does not affect other items in the batch.

    Args:
        item_id: RawItem ID to process.
        router: Initialized ModelRouter instance.
        deduper: Initialized SemanticDeduplicator instance.
        existing_embeddings: (N, 384) matrix of previously processed article
            embeddings for semantic dedup comparison.

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

        # Prevent race condition: only process items still in "pending" status
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
        # --- Phase 2: Layer 3 Semantic Dedup ---
        if deduper.is_duplicate(item.title, existing_embeddings):
            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(RawItem).where(RawItem.id == item_id)
                )
                item = result.scalar_one_or_none()
                if item:
                    item.status = "duplicate"
                    await db.commit()
            logger.info("Item %d is a semantic duplicate — skipped", item_id)
            return "duplicate"

        content = item.content_normalized or item.content_raw or ""

        # --- Phase 3: Classification + Tagging ---
        # Paper sources: use LLM for tags but force "研究" category
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
        # Mark item as failed with error details
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
        2. Pre-load recent article embeddings for dedup window (3 days)
        3. For each item (per-item session, error-isolated):
            a. Semantic dedup check
            b. LLM classification + tagging → category, tags
            c. LLM summarization → Chinese summary (150-300 chars)
            d. LLM scoring → recommendation score + reason
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

    # Initialize shared resources
    clients = LLMClients.from_settings(settings)
    router = ModelRouter(clients=clients, settings=settings)
    deduper = SemanticDeduplicator()

    # Pre-load recent embeddings for semantic dedup window (3 days)
    try:
        existing_embeddings = await get_recent_embeddings(days=3)
        logger.info(
            "Loaded %d recent article embeddings for dedup window",
            len(existing_embeddings) if len(existing_embeddings.shape) > 1 else 0,
        )
    except Exception as exc:
        logger.warning("Failed to load recent embeddings: %s — proceeding without", exc)
        existing_embeddings = np.array([])

    # Poll pending items
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(RawItem)
            .where(RawItem.status == "pending")
            .where(
                RawItem.retry_count < settings.MAX_RETRIES
            )
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
    embeddings_cache: list[np.ndarray] = []
    if len(existing_embeddings) > 0:
        embeddings_cache.append(existing_embeddings)

    processed_count = 0
    for item in pending_items:
        # Build consolidated embeddings matrix for this item
        if embeddings_cache:
            current_embeddings = np.vstack(embeddings_cache)
        else:
            current_embeddings = np.array([])

        status = await process_single_item(
            item_id=item.id,
            router=router,
            deduper=deduper,
            existing_embeddings=current_embeddings,
        )

        # Update embeddings cache for subsequent items in this batch
        if status == "processed":
            processed_count += 1
            emb = deduper.encode([item.title])
            embeddings_cache.append(emb)

    # Cleanup LLM client
    await clients.close()

    logger.info("Batch complete: %d/%d items processed", processed_count, len(pending_items))
    return processed_count
