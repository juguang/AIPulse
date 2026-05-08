"""RSS/Atom feed fetcher using feedparser + httpx."""

from datetime import datetime, timezone
from typing import Any
import feedparser
import httpx

from app.crawler.base import BaseFetcher
from app.crawler.registry import register_fetcher
from app.crawler.normalizer import ensure_timezone


@register_fetcher("rss")
class RSSFetcher(BaseFetcher):
    """Fetches articles from RSS/Atom feeds."""

    async def fetch(self) -> list[dict[str, Any]]:
        url = self.source.url or self.source.config.get("feed_url", "")
        if not url:
            return []

        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            resp = await client.get(url, headers={"User-Agent": "AI-Pulse/1.0"})
            resp.raise_for_status()

        feed = feedparser.parse(resp.text)
        items = []
        for entry in feed.entries:
            published = entry.get("published_parsed") or entry.get("updated_parsed")
            pub_dt = (
                datetime(*published[:6], tzinfo=timezone.utc) if published else None
            )
            link = (entry.get("link") or "").strip()
            items.append(
                {
                    "guid": entry.get("id") or link,
                    "title": (entry.get("title") or "").strip(),
                    "url": link,
                    "content_raw": (
                        entry.get("content", [{}])[0].get("value")
                        or entry.get("summary")
                        or ""
                    ),
                    "author": (entry.get("author") or "").strip() or None,
                    "published_at": ensure_timezone(pub_dt),
                    "raw_data": {
                        "source": url,
                        "entry_id": entry.get("id"),
                    },
                }
            )
        return items
