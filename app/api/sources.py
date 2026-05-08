from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.source_config import SourceConfig
from app.schemas.sources import SourceConfigCreate, SourceConfigResponse

router = APIRouter(prefix="/api/v1/sources", tags=["sources"])


@router.get("", response_model=list[SourceConfigResponse])
async def list_sources(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SourceConfig).order_by(SourceConfig.name))
    sources = result.scalars().all()
    return [SourceConfigResponse.model_validate(s) for s in sources]


@router.get("/{source_id}", response_model=SourceConfigResponse)
async def get_source(source_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(SourceConfig).where(SourceConfig.id == source_id)
    )
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    return SourceConfigResponse.model_validate(source)


@router.post("", response_model=SourceConfigResponse, status_code=201)
async def create_source(
    source_data: SourceConfigCreate, db: AsyncSession = Depends(get_db)
):
    source = SourceConfig(**source_data.model_dump())
    db.add(source)
    await db.commit()
    await db.refresh(source)
    return SourceConfigResponse.model_validate(source)
