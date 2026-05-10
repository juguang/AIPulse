"""OpenCLI-based fetcher for sources like HackerNews, arXiv, etc."""

import json
import asyncio
import hashlib
import shutil
from datetime import datetime, timezone, timedelta
from typing import Any

from app.crawler.base import BaseFetcher
from app.crawler.registry import register_fetcher
from app.crawler.normalizer import ensure_timezone

OPENCLI_BIN = shutil.which("opencli") or "opencli"


async def _run_opencli(*args: str) -> list[dict[str, Any]]:
    """Run opencli command and parse JSON output."""
    proc = await asyncio.create_subprocess_exec(
        OPENCLI_BIN,
        *args,
        "-f",
        "json",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(f"opencli failed: {stderr.decode()}")
    return json.loads(stdout.decode())


def _scatter_time(dt: datetime | None, seed: str = "") -> datetime | None:
    """Add a pseudo-random minute offset to date-only timestamps.

    Academic papers often only have a date (midnight). This spreads them
    across the day using the paper ID as a seed, so they don't all stack
    at 00:00 in the timeline view.
    """
    if dt is None:
        return None
    if dt.hour != 0 or dt.minute != 0 or dt.second != 0:
        return dt  # Already has a time component
    h = int(hashlib.md5(seed.encode()).hexdigest(), 16) if seed else 0
    offset = timedelta(hours=h % 14 + 6, minutes=h // 14 % 60)  # 06:00 - 19:59
    return dt + offset


@register_fetcher("hackernews")
class HackerNewsFetcher(BaseFetcher):
    """HackerNews fetcher via opencli."""

    async def fetch(self) -> list[dict[str, Any]]:
        limit = self.get_config("limit", 30)
        data = await _run_opencli("hackernews", "top")
        items = []
        for item in data[:limit]:
            items.append(
                {
                    "guid": str(item.get("id", "")),
                    "title": (item.get("title") or "").strip(),
                    "url": (item.get("url") or f"https://news.ycombinator.com/item?id={item.get('id')}"),
                    "content_raw": (item.get("text") or item.get("description") or ""),
                    "author": (item.get("by") or item.get("author") or ""),
                    "published_at": ensure_timezone(
                        datetime.fromtimestamp(item.get("time", 0), tz=timezone.utc)
                        if item.get("time")
                        else None
                    ),
                    "raw_data": {"source": "hackernews"},
                }
            )
        return items

