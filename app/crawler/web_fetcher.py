"""Generic HTTP web scraper fetcher using httpx + BeautifulSoup."""

from datetime import datetime, timezone
from typing import Any
import httpx

from app.crawler.base import BaseFetcher
from app.crawler.registry import register_fetcher
from app.crawler.normalizer import ensure_timezone, html_to_text


@register_fetcher("web")
class WebFetcher(BaseFetcher):
    """Generic web scraper for HTML pages."""

    async def fetch(self) -> list[dict[str, Any]]:
        url = self.source.url or self.source.config.get("page_url", "")
        if not url:
            return []

        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            resp = await client.get(
                url,
                headers={"User-Agent": "AI-Pulse/1.0"},
            )
            resp.raise_for_status()

        text = html_to_text(resp.text)
        title = self._extract_title(resp.text) or url

        return [
            {
                "guid": url,
                "title": title,
                "url": url,
                "content_raw": text,
                "author": None,
                "published_at": ensure_timezone(None),
                "raw_data": {"source": url},
            }
        ]

    def _extract_title(self, html: str) -> str | None:
        import re
        m = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
        return m.group(1).strip() if m else None
