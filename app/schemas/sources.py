from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class SourceConfigCreate(BaseModel):
    name: str
    type: str  # rss/x/web
    url: str
    active: bool = True
    crawl_interval: int = 30


class SourceConfigResponse(BaseModel):
    id: int
    name: str
    type: str
    url: str
    active: bool
    crawl_interval: int
    last_crawled_at: Optional[datetime] = None
    last_error: Optional[str] = None
    consecutive_failures: int = 0
    health_score: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
