"""HuggingFace daily papers fetcher using huggingface_hub."""

from datetime import datetime, timezone
from typing import Any

from app.crawler.base import BaseFetcher
from app.crawler.registry import register_fetcher
from app.crawler.normalizer import ensure_timezone


@register_fetcher("huggingface")
class HFFetcher(BaseFetcher):
    """Fetches daily trending papers from HuggingFace."""

    async def fetch(self) -> list[dict[str, Any]]:
        try:
            from huggingface_hub import HfApi
        except ImportError:
            return []

        api = HfApi()
        limit = self.get_config("limit", 20)

        try:
            papers = list(api.list_daily_papers())
        except Exception:
            return []

        items = []
        for paper in papers[:limit]:
            items.append(
                {
                    "guid": paper.get("id", "") or paper.get("arxivId", ""),
                    "title": (paper.get("title") or "").strip(),
                    "url": (
                        f"https://arxiv.org/abs/{paper['arxivId']}"
                        if paper.get("arxivId")
                        else paper.get("url", "")
                    ),
                    "content_raw": (paper.get("summary") or ""),
                    "author": ", ".join(paper.get("authors", [])),
                    "published_at": ensure_timezone(
                        datetime.fromisoformat(paper["published"].replace("Z", "+00:00"))
                        if paper.get("published")
                        else None
                    ),
                    "raw_data": {
                        "source": "huggingface",
                        "paper_id": paper.get("id"),
                    },
                }
            )
        return items
