from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class ImageCache(Base):
    """Cached image entry with original URL and proxy path."""

    __tablename__ = "image_cache"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    original_url: Mapped[str] = mapped_column(
        Text, unique=True, nullable=False, index=True
    )
    proxy_path: Mapped[str] = mapped_column(String(512), nullable=False)
    cached_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    content_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
