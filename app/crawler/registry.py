"""Fetcher registry — maps source type to fetcher class via decorator."""

from typing import Type

from app.crawler.base import BaseFetcher

_fetcher_registry: dict[str, Type[BaseFetcher]] = {}


def register_fetcher(source_type: str):
    """装饰器：将 Fetcher 类注册到指定 source_type"""

    def decorator(cls: Type[BaseFetcher]) -> Type[BaseFetcher]:
        _fetcher_registry[source_type] = cls
        return cls

    return decorator


def get_fetcher(source_type: str) -> Type[BaseFetcher]:
    """根据 source_type 查找对应的 Fetcher 类"""
    fetcher = _fetcher_registry.get(source_type)
    if not fetcher:
        raise ValueError(
            f"Unknown source type: {source_type}. Available: {list(_fetcher_registry.keys())}"
        )
    return fetcher


def list_fetcher_types() -> list[str]:
    """返回所有已注册的 source type 列表"""
    return list(_fetcher_registry.keys())
