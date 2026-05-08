"""X/Twitter fetcher via OpenCLI (cookie-based auth)."""

import json
import asyncio
from datetime import datetime, timezone
from typing import Any

from app.crawler.base import BaseFetcher
from app.crawler.registry import register_fetcher
from app.crawler.normalizer import ensure_timezone

OPENCLI_BIN = "OPENCLI_BIN"


@register_fetcher("twitter")
class TwitterFetcher(BaseFetcher):
    """Fetches tweets from X/Twitter using OpenCLI.

    Requires Chrome login cookies (OpenCLI reuses browser session).
    """

    async def fetch(self) -> list[dict[str, Any]]:
        search_query = self.source.config.get("query", "AI")
        limit = self.source.config.get("limit", 20)

        proc = await asyncio.create_subprocess_exec(
            OPENCLI_BIN,
            "twitter",
            "search",
            search_query,
            "-f",
            "json",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(f"opencli twitter failed: {stderr.decode()}")

        data = json.loads(stdout.decode())
        tweets = data if isinstance(data, list) else data.get("tweets", data.get("data", [data]))
        items = []
        for t in tweets[:limit]:
            created_at = None
            if t.get("created_at"):
                try:
                    created_at = datetime.fromisoformat(t["created_at"].replace("Z", "+00:00"))
                except (ValueError, TypeError):
                    pass

            items.append(
                {
                    "guid": t.get("id_str") or t.get("id", ""),
                    "title": (t.get("full_text") or t.get("text") or "")[:200],
                    "url": f"https://x.com/i/web/status/{t.get('id_str') or t.get('id', '')}",
                    "content_raw": t.get("full_text") or t.get("text") or "",
                    "author": (
                        t.get("user", {}).get("screen_name")
                        or t.get("screen_name")
                        or ""
                    ),
                    "published_at": ensure_timezone(created_at),
                    "raw_data": {"source": "twitter", "query": search_query},
                }
            )
        return items
