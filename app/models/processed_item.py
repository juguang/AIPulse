from datetime import datetime
from typing import Optional, Dict
from sqlalchemy import (
    BigInteger,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class ProcessedItem(Base):
    """AI-processed content with summary, tags, and recommendation score."""

    __tablename__ = "processed_items"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    raw_item_id: Mapped[int] = mapped_column(
        ForeignKey("raw_items.id"), unique=True, nullable=False, index=True
    )
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tags: Mapped[Optional[Dict]] = mapped_column(JSONB, nullable=True, default=[])
    category: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, index=True
    )  # 模型/产品/行业/论文/技巧
    recommended_score: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, default=0.0
    )
    recommendation_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    llm_model_used: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    input_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=0)
    output_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=0)
    cost_usd: Mapped[Optional[float]] = mapped_column(Float, nullable=True, default=0.0)
    processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    raw_item = relationship("RawItem", back_populates="processed")
