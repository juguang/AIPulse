from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.processed_item import ProcessedItem
from app.models.raw_item import RawItem
from app.models.source_config import SourceConfig
from app.schemas.items import (
    FeedItemResponse,
    PaginatedResponse,
    RawItemCreate,
    RawItemResponse,
)

router = APIRouter(prefix="/api/v1/items", tags=["items"])


@router.get("", response_model=PaginatedResponse[FeedItemResponse])
async def list_items(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None, max_length=200),
    db: AsyncSession = Depends(get_db),
):
    """返回 feed 信息流数据，支持分类筛选、搜索和分页。

    使用三表 JOIN (ProcessedItem + RawItem + SourceConfig) 获取前端所需的完整字段。
    当 category 不为 None 且不为 "全部" 时按分类筛选。
    当 search 不为空时按标题或标准化内容模糊搜索。
    """
    # Build query: only show processed items (with tags/category/score)
    base_query = (
        select(
            RawItem,
            ProcessedItem,
            SourceConfig.name,
        )
        .join(SourceConfig, RawItem.source_id == SourceConfig.id)
        .join(ProcessedItem, ProcessedItem.raw_item_id == RawItem.id)
        .where(RawItem.status == "processed")
    )

    # Category filter (only for processed items)
    if category and category != "全部":
        base_query = base_query.where(ProcessedItem.category == category)

    # Search
    if search:
        pattern = f"%{search}%"
        base_query = base_query.where(
            RawItem.title.ilike(pattern)
            | RawItem.content_normalized.ilike(pattern)
        )

    base_query = base_query.order_by(RawItem.published_at.desc())

    # Count
    count_query = select(func.count()).select_from(RawItem).join(
        SourceConfig, RawItem.source_id == SourceConfig.id
    ).join(ProcessedItem, ProcessedItem.raw_item_id == RawItem.id).where(
        RawItem.status == "processed"
    )
    if category and category != "全部":
        count_query = count_query.where(ProcessedItem.category == category)
    if search:
        pattern = f"%{search}%"
        count_query = count_query.where(
            RawItem.title.ilike(pattern)
            | RawItem.content_normalized.ilike(pattern)
        )

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    offset = (page - 1) * page_size
    query = base_query.offset(offset).limit(page_size)
    result = await db.execute(query)
    rows = result.all()

    items = []
    for raw_item, processed_item, source_name in rows:
        extra = raw_item.extra_data or {}

        items.append(
            FeedItemResponse(
                id=raw_item.id,
                title=raw_item.title,
                source_url=raw_item.source_url,
                source_name=source_name,
                author=raw_item.author,
                published_at=raw_item.published_at,
                summary=processed_item.summary,
                tags=processed_item.tags if isinstance(processed_item.tags, list) else None,
                category=processed_item.category,
                recommended_score=processed_item.recommended_score,
                recommendation_reason=processed_item.recommendation_reason,
                image_url=extra.get("image_url"),
                created_at=raw_item.created_at,
            )
        )

    return PaginatedResponse[FeedItemResponse](
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=max(1, (total + page_size - 1) // page_size),
    )


@router.get("/{item_id}", response_model=RawItemResponse)
async def get_item(item_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(RawItem).where(RawItem.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return RawItemResponse.model_validate(item)


@router.post("", response_model=RawItemResponse, status_code=201)
async def create_item(item_data: RawItemCreate, db: AsyncSession = Depends(get_db)):
    item = RawItem(**item_data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return RawItemResponse.model_validate(item)
