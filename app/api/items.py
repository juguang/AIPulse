from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.raw_item import RawItem
from app.schemas.items import RawItemCreate, RawItemResponse, PaginatedResponse

router = APIRouter(prefix="/api/v1/items", tags=["items"])


@router.get("", response_model=PaginatedResponse)
async def list_items(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(RawItem)
    if status:
        query = query.where(RawItem.status == status)
    query = query.order_by(RawItem.published_at.desc())

    count_query = select(func.count()).select_from(RawItem)
    if status:
        count_query = count_query.where(RawItem.status == status)
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return PaginatedResponse(
        items=[RawItemResponse.model_validate(item) for item in items],
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
