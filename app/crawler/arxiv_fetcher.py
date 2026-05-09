"""ArXiv fetcher using official Arxiv API (proper timestamps).

Arxiv API returns real submission timestamps, unlike the RSS feed which
batches all papers to midnight.
"""

import asyncio
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Any

import httpx

from app.crawler.base import BaseFetcher
from app.crawler.registry import register_fetcher
from app.crawler.normalizer import ensure_timezone

ARXIV_API = "https://export.arxiv.org/api/query"
NS = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}


@register_fetcher("arxiv")
class ArxivAPIFetcher(BaseFetcher):
    """Fetches recent AI papers from Arxiv API with real timestamps."""

    async def fetch(self) -> list[dict[str, Any]]:
        category = self.get_config("category", "cs.AI")
        limit = self.get_config("limit", 50)

        query = f"cat:{category}&sortBy=submittedDate&sortOrder=descending"
        url = f"{ARXIV_API}?search_query={query}&max_results={limit}"

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(url)
            resp.raise_for_status()

        root = ET.fromstring(resp.text)
        items = []
        for entry in root.findall("atom:entry", NS):
            paper_id = entry.find("atom:id", NS).text.strip() if entry.find("atom:id", NS) is not None else ""
            title = entry.find("atom:title", NS)
            published = entry.find("atom:published", NS)
            summary = entry.find("atom:summary", NS)
            authors = entry.findall("atom:author", NS)

            pub_dt = None
            if published is not None and published.text:
                try:
                    pub_dt = datetime.fromisoformat(published.text.replace("Z", "+00:00"))
                except (ValueError, TypeError):
                    pass

            author_names = []
            for a in authors:
                name = a.find("atom:name", NS)
                if name is not None and name.text:
                    author_names.append(name.text.strip())

            abs_url = paper_id.replace("http://", "https://") if paper_id else ""

            items.append(
                {
                    "guid": paper_id,
                    "title": (title.text.strip() if title is not None and title.text else ""),
                    "url": abs_url,
                    "content_raw": (summary.text.strip() if summary is not None and summary.text else ""),
                    "author": ", ".join(author_names) if author_names else None,
                    "published_at": ensure_timezone(pub_dt),
                    "raw_data": {"source": "arxiv_api"},
                }
            )
        return items
