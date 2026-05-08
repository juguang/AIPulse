from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class RawItemCreate(BaseModel):
    source_id: int
    source_url: str
    guid: Optional[str] = None
    title: str
    content_raw: Optional[str] = None
    content_normalized: Optional[str] = None
    author: Optional[str] = None
    published_at: datetime
    content_hash: str
    metadata: Optional[Dict[str, Any]] = {}


class RawItemResponse(BaseModel):
    id: int
    source_id: int
    source_url: str
    guid: Optional[str] = None
    title: str
    content_raw: Optional[str] = None
    content_normalized: Optional[str] = None
    author: Optional[str] = None
    published_at: datetime
    fetched_at: datetime
    content_hash: str
    status: str
    error_message: Optional[str] = None
    retry_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class PaginatedResponse(BaseModel):
    items: List[RawItemResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
