"""Generic OpenCLI web fetcher for JavaScript-rendered pages.

Uses `opencli web read` to render JS-heavy pages and extract article content.
Also supports sitemap parsing for URLs with embedded dates.

Good for: 量子位, 机器之心, and other SPA-based Chinese media sites.
"""

import json
import asyncio
import re
import gzip
import shutil
from datetime import datetime, timezone, timedelta
from typing import Any
from urllib.parse import urljoin

import httpx

from app.crawler.base import BaseFetcher
from app.crawler.registry import register_fetcher
from app.crawler.normalizer import ensure_timezone

OPENCLI_BIN = shutil.which("opencli") or "opencli"


async def _web_read(url: str) -> str:
    """Fetch a web page via OpenCLI web read, returns markdown content."""
    proc = await asyncio.create_subprocess_exec(
        OPENCLI_BIN, "web", "read", "--url", url, "-f", "json",
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(f"opencli web read failed: {stderr.decode()[:500]}")
    result = json.loads(stdout.decode())
    if isinstance(result, list) and len(result) > 0:
        filepath = result[0].get("saved", "")
        if filepath:
            try:
                with open(filepath, encoding="utf-8") as f:
                    return f.read()
            except FileNotFoundError:
                pass
    return ""


MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}


def _extract_date_from_text(text: str) -> datetime | None:
    """Extract date from text like 'Apr 16, 2026' or 'ProductApr 16, 2026'."""
    m = re.search(r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+(\d{1,2}),?\s+(\d{4})", text, re.IGNORECASE)
    if m:
        month = MONTHS.get(m[1].lower()[:3])
        if month:
            try:
                return datetime(int(m[3]), month, int(m[2]), tzinfo=timezone.utc)
            except ValueError:
                pass
    return None


def _parse_articles_from_markdown(md: str, base_url: str = "") -> list[dict[str, Any]]:
    """Parse article titles and links from markdown content."""
    items = []
    seen_urls = set()

    def resolve_url(u: str) -> str:
        if u.startswith("http"):
            return u
        if base_url and u.startswith("/"):
            return base_url.rstrip("/") + u
        if base_url and not u.startswith("#"):
            return base_url.rstrip("/") + "/" + u.lstrip("/")
        return u

    # Find links and their surrounding text (up to 200 chars after the link)
    pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
    for m in pattern.finditer(md):
        title = m.group(1).strip()
        url = resolve_url(m.group(2).strip())
        if any(
            skip in url for skip in ["javascript:", "cdn.", ".css", "avatar", "logo", "icon", "#"]
        ):
            continue
        if not title or len(title) < 4 or url in seen_urls:
            continue
        seen_urls.add(url)

        # Look for date in surrounding text (150 chars before and after)
        start = max(0, m.start() - 150)
        end = min(len(md), m.end() + 150)
        context = md[start:end]
        pub_date = _extract_date_from_text(context)

        items.append({
            "guid": url, "title": title[:300], "url": url,
            "content_raw": "", "author": None,
            "published_at": ensure_timezone(pub_date),
            "raw_data": {"source": "opencli_web"},
        })
    return items


def _extract_date_from_url(url: str) -> datetime | None:
    """Extract date from URL patterns like /2026-05-09-11 or /2024-7-31."""
    # Match YYYY-MM-DD (with optional single-digit month/day)
    m = re.search(r"/(\d{4})-(\d{1,2})-(\d{1,2})(?:[^0-9]|$)", url)
    if m:
        try:
            return datetime(int(m[1]), int(m[2]), int(m[3]), tzinfo=timezone.utc)
        except ValueError:
            return None
    return None


async def _fetch_sitemap_urls(sitemap_url: str, limit: int = 50) -> list[dict[str, Any]]:
    """Fetch article URLs from a sitemap XML, extracting real timestamps."""
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            resp = await client.get(sitemap_url, headers={"User-Agent": "AI-Pulse/1.0"})
            resp.raise_for_status()
            content = resp.content
            if sitemap_url.endswith(".gz"):
                content = gzip.decompress(content)
    except Exception:
        return []

    import xml.etree.ElementTree as ET

    items = []
    seen = set()
    try:
        root = ET.fromstring(content.decode())
        ns = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        for url_elem in root.findall("ns:url", ns):
            loc = url_elem.findtext("ns:loc", "", ns).strip()
            lastmod = url_elem.findtext("ns:lastmod", "", ns).strip()

            # Fix double-domain URLs
            if loc.count("http") > 1:
                loc = "https://" + loc.rsplit("https://", 1)[-1]

            # Only process article pages
            if "/articles/" not in loc:
                continue
            if loc in seen:
                continue
            seen.add(loc)

            # Only use URL-embedded dates (lastmod is unreliable for sitemaps)
            pub_date = _extract_date_from_url(loc)
            if pub_date is None:
                continue  # Skip articles without dates in URL

            # Skip old articles
            if pub_date < datetime.now(timezone.utc) - timedelta(days=7):
                continue

            slug = loc.rstrip("/").rsplit("/", 1)[-1]
            items.append({
                "guid": loc, "title": slug.replace("-", " ")[:100], "url": loc,
                "content_raw": "", "author": None,
                "published_at": ensure_timezone(pub_date),
                "raw_data": {"source": "sitemap"},
            })
    except ET.ParseError:
        return []

    # Sort by date descending, take recent ones
    items.sort(key=lambda x: x["published_at"] or datetime.min, reverse=True)
    return items[:limit]


@register_fetcher("opencli_web")
class OpenCLIWebFetcher(BaseFetcher):
    """Fetcher for JS-rendered websites using OpenCLI or sitemap."""

    async def fetch(self) -> list[dict[str, Any]]:
        url = self.source.url
        if not url:
            return []
        limit = self.get_config("limit", 30)

        # Try sitemap first (URL contains "sitemap" or stored as config)
        sitemap = url if "sitemap" in url else self.get_config("sitemap", "")
        if sitemap and "sitemap" in sitemap:
            items = await _fetch_sitemap_urls(sitemap, limit=limit)
            if items:
                return items

        # Fallback: use OpenCLI web read for JS-rendered pages
        markdown = await _web_read(url)
        if not markdown:
            return []

        items = _parse_articles_from_markdown(markdown, base_url=url)
        return items[:limit]
