"""HuggingFace Daily Papers fetcher using official API.

API: GET https://huggingface.co/api/daily_papers
Returns 50 papers with real publishedAt timestamps.
"""

from datetime import datetime, timezone
from typing import Any
import httpx

from app.crawler.base import BaseFetcher
from app.crawler.registry import register_fetcher
from app.crawler.normalizer import ensure_timezone


@register_fetcher("hf_papers")
class HFDailyPapersFetcher(BaseFetcher):
    """Fetches daily trending papers from HuggingFace API."""

    async def fetch(self) -> list[dict[str, Any]]:
        limit = self.get_config("limit", 30)
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                "https://huggingface.co/api/daily_papers",
                headers={"User-Agent": "AI-Pulse/1.0"},
            )
            if resp.status_code == 403:
                return []
            resp.raise_for_status()
            data = resp.json()

        items = []
        for entry in data[:limit]:
            paper = entry.get("paper", {})
            paper_id = paper.get("id", "")
            pub_date = None
            if paper.get("publishedAt"):
                try:
                    pub_date = datetime.fromisoformat(paper["publishedAt"].replace("Z", "+00:00"))
                except (ValueError, TypeError):
                    pass

            authors = [a.get("name", "") for a in paper.get("authors", []) if a.get("name")]

            items.append({
                "guid": f"hf_{paper_id}",
                "title": (paper.get("title") or "").strip()[:300],
                "url": f"https://arxiv.org/abs/{paper_id}" if paper_id else "",
                "content_raw": (paper.get("summary") or ""),
                "author": ", ".join(authors) if authors else None,
                "published_at": ensure_timezone(pub_date),
                "raw_data": {"source": "hf_papers", "paper_id": paper_id},
            })
        return items
