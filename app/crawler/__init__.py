"""Multi-source content crawling infrastructure.

Provides abstract fetcher base class, fetcher registry (decorator-based),
content normalizers, and concrete fetcher implementations for:
- RSS/Atom feeds (feedparser)
- OpenCLI-based sources (HackerNews, arXiv, Twitter/X)
- HTTP web scraping (httpx + BeautifulSoup)
- HuggingFace daily papers

Import all fetcher modules so @register_fetcher decorators execute.
"""

from app.crawler import rss_fetcher  # noqa: F401
from app.crawler import opencli_fetcher  # noqa: F401
from app.crawler import arxiv_fetcher  # noqa: F401
from app.crawler import hn_fetcher  # noqa: F401
from app.crawler import twitter_fetcher  # noqa: F401
from app.crawler import hf_fetcher  # noqa: F401
from app.crawler import web_fetcher  # noqa: F401
