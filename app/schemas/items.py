from datetime import datetime
from typing import Generic, Optional, Dict, Any, List, TypeVar

from pydantic import BaseModel, Field


T = TypeVar("T")


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


class FeedItemResponse(BaseModel):
    """联合响应模型：合并 processed_item + raw_item + source_config.name 的字段。

    供前端信息流展示使用，包含完整的内容摘要、标签、评分和来源信息。
    """

    id: int
    title: str
    source_url: str
    source_name: str
    author: Optional[str] = None
    published_at: datetime
    summary: Optional[str] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None
    recommended_score: Optional[float] = 0.0
    recommendation_reason: Optional[str] = None
    image_url: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
