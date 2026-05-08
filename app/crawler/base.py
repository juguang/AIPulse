"""Abstract base class for all source fetchers."""

from abc import ABC, abstractmethod
from typing import Any

from app.models.source_config import SourceConfig


class BaseFetcher(ABC):
    """每个源类型实现一个 BaseFetcher 子类。

    约定：
    - source.type 决定使用哪个 fetcher（通过 Registry 映射）
    - fetch() 返回规范化后的 dict 列表，每个 dict 对应一条 raw_item 数据
    - 异常传播给调用者（coordinator 处理）
    """

    def __init__(self, source: SourceConfig):
        self.source = source

    @abstractmethod
    async def fetch(self) -> list[dict[str, Any]]:
        """获取并解析内容，返回规范化后的 article dict 列表。

        每个 dict 必须包含：
        - guid: str (源内唯一 ID)
        - title: str
        - url: str
        - content_raw: str | None
        - author: str | None
        - published_at: datetime (带时区)
        - raw_data: dict (原始响应数据，供后续重处理)
        """
