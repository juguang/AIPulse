"""HackerNews fetcher using Firebase API (official, no auth required).

HN Firebase API returns proper Unix timestamps in the `time` field.
"""

import asyncio
from datetime import datetime, timezone
from typing import Any

import httpx

from app.crawler.base import BaseFetcher
from app.crawler.registry import register_fetcher
from app.crawler.normalizer import ensure_timezone

HN_TOP_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"


@register_fetcher("hackernews")
class HackerNewsFetcher(BaseFetcher):
    """Fetches top stories from HackerNews via Firebase API."""

    async def fetch(self) -> list[dict[str, Any]]:
        limit = self.get_config("limit", 30)

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(HN_TOP_URL)
            resp.raise_for_status()
            ids = resp.json()[:limit]

            tasks = [self._fetch_item(client, iid) for iid in ids]
            items = await asyncio.gather(*tasks, return_exceptions=True)

        return [it for it in items if isinstance(it, dict)]

    async def _fetch_item(self, client: httpx.AsyncClient, item_id: int) -> dict[str, Any] | None:
        try:
            resp = await client.get(HN_ITEM_URL.format(item_id))
            resp.raise_for_status()
            data = resp.json()
            if not data or not data.get("title"):
                return None

            ts = data.get("time", 0)
            return {
                "guid": str(data["id"]),
                "title": (data.get("title") or "").strip(),
                "url": (data.get("url") or f"https://news.ycombinator.com/item?id={data['id']}"),
                "content_raw": (data.get("text") or ""),
                "author": data.get("by", ""),
                "published_at": ensure_timezone(
                    datetime.fromtimestamp(ts, tz=timezone.utc) if ts else None
                ),
                "raw_data": {"source": "hackernews", "score": data.get("score")},
            }
        except Exception:
            return None
