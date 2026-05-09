"""Claude Blog (claude.com/blog) fetcher.

The claude.com/blog is a Webflow SPA that doesn't provide RSS.
This fetcher parses the raw HTML to extract blog post URLs, titles, and dates.

Usage:
    Source config: type="claude_blog", url="https://claude.com/blog"
"""

import logging
import re
from datetime import datetime, timezone, timedelta
from typing import Any

import httpx

from app.crawler.base import BaseFetcher
from app.crawler.registry import register_fetcher
from app.crawler.normalizer import ensure_timezone

BLOG_URL = "https://claude.com/blog"
BASE_URL = "https://claude.com"
MAX_AGE_DAYS = 14

logger = logging.getLogger(__name__)

MONTH_MAP = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}


def _extract_articles(html: str) -> list[dict[str, Any]]:
    """Extract blog articles from the HTML page content."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=MAX_AGE_DAYS)

    # Find all unique blog post slugs
    slugs = set(re.findall(r'href="(/blog/[^/"\']+)"', html))

    items = []
    for slug in sorted(slugs):
        # Find context around this slug (1000 chars before)
        idx = html.find(slug)
        if idx == -1:
            continue
        chunk = html[max(0, idx - 1000):idx + 100]

        # Extract dates
        pub_date = None
        date_match = re.search(
            r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+(\d{1,2}),?\s+(\d{4})",
            chunk, re.IGNORECASE,
        )
        if date_match:
            month = MONTH_MAP.get(date_match[1].lower()[:3])
            if month:
                try:
                    pub_date = datetime(int(date_match[3]), month, int(date_match[2]), tzinfo=timezone.utc)
                except ValueError:
                    pass

        # Skip old articles
        if pub_date and pub_date < cutoff:
            continue

        # Extract title: look for visible text in nearby elements
        title = None
        texts = re.findall(r'>([^<]{8,150})<', chunk)
        slug_title = slug.replace("/blog/", "").replace("-", " ").title()

        # Known non-article labels to skip
        skip_labels = {"product announcements", "claude code", "enterprise ai", "agents",
                       "read more", "usecase", "category", "product", "sort by", "page"}

        for t in texts:
            t = t.strip()
            if not t or t.lower() in skip_labels or t == "Read more":
                continue
            if re.search(r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{1,2}", t):
                continue
            if len(t) >= 15:
                title = t
                break

        url = BASE_URL + slug
        items.append({
            "guid": url,
            "title": (title or slug_title)[:300],
            "url": url,
            "content_raw": "",
            "author": "Anthropic",
            "published_at": ensure_timezone(pub_date),
            "raw_data": {"source": "claude_blog"},
        })

    # Deduplicate by URL
    seen = set()
    unique_items = []
    for item in items:
        if item["url"] not in seen:
            seen.add(item["url"])
            unique_items.append(item)

    # Sort by date descending
    unique_items.sort(key=lambda x: x["published_at"] or datetime.min, reverse=True)
    return unique_items


@register_fetcher("claude_blog")
class ClaudeBlogFetcher(BaseFetcher):
    """Fetcher for claude.com/blog (Webflow SPA without RSS)."""

    async def fetch(self) -> list[dict[str, Any]]:
        url = self.source.url or BLOG_URL
        limit = self.get_config("limit", 30)

        try:
            async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
                resp = await client.get(url, headers={
                    "User-Agent": "Mozilla/5.0 (compatible; AI-Pulse/1.0)",
                    "Accept": "text/html,application/xhtml+xml",
                })
                resp.raise_for_status()
                html = resp.text
        except Exception as e:
            logger.warning("Failed to fetch %s: %s", url, e)
            return []

        items = _extract_articles(html)
        return items[:limit]
