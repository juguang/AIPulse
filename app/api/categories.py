from fastapi import APIRouter, Depends
from sqlalchemy import distinct, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.processed_item import ProcessedItem

router = APIRouter(prefix="/api/v1/categories", tags=["categories"])


@router.get("")
async def list_categories(db: AsyncSession = Depends(get_db)):
    """返回所有可用分类的去重列表，始终包含"全部"作为第一个选项。"""
    query = (
        select(distinct(ProcessedItem.category))
        .where(ProcessedItem.category.isnot(None))
        .order_by(ProcessedItem.category)
    )
    result = await db.execute(query)
    categories = [row[0] for row in result.all() if row[0]]
    # 始终包含 "全部" 作为第一个选项
    return ["全部"] + categories
