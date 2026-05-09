"""GitHub trending fetcher using GitHub API.

Fetches popular AI/ML repositories sorted by stars.
"""

from datetime import datetime, timezone
from typing import Any
import httpx

from app.crawler.base import BaseFetcher
from app.crawler.registry import register_fetcher
from app.crawler.normalizer import ensure_timezone


@register_fetcher("github")
class GitHubTrendingFetcher(BaseFetcher):
    """Fetches trending AI repositories from GitHub."""

    async def fetch(self) -> list[dict[str, Any]]:
        limit = self.get_config("limit", 20)
        query = self.get_config("query", "ai language:python pushed:>2026-05-01")
        query += " sort:stars desc"

        url = f"https://api.github.com/search/repositories"
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "AI-Pulse/1.0",
        }

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                url,
                params={"q": query, "per_page": limit, "sort": "stars"},
                headers=headers,
            )
            if resp.status_code == 403:
                return []  # Rate limited
            resp.raise_for_status()
            data = resp.json()

        items = []
        for repo in data.get("items", [])[:limit]:
            items.append(
                {
                    "guid": f"github_{repo['id']}",
                    "title": f"{repo['full_name']}: {repo.get('description', '') or ''}"[:300],
                    "url": repo["html_url"],
                    "content_raw": repo.get("description") or "",
                    "author": repo.get("owner", {}).get("login", ""),
                    "published_at": ensure_timezone(
                        datetime.fromisoformat(repo["created_at"].replace("Z", "+00:00"))
                        if repo.get("created_at")
                        else None
                    ),
                    "raw_data": {
                        "source": "github",
                        "stars": repo.get("stargazers_count"),
                        "language": repo.get("language"),
                    },
                }
            )
        return items
