"""Multi-source content crawling infrastructure.

Provides abstract fetcher base class, fetcher registry (decorator-based),
content normalizers, and concrete fetcher implementations for:
- RSS/Atom feeds (feedparser)
- OpenCLI-based sources (HackerNews, arXiv)
- HTTP web scraping (httpx + BeautifulSoup)
- HuggingFace daily papers
"""
