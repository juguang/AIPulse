"""Content normalization utilities.

Provides URL canonicalization, content hash generation, HTML-to-text
conversion, and timezone-aware datetime handling.
"""

import hashlib
import re
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urlparse


def compute_content_hash(title: str, url: str) -> str:
    """基于标题+URL 生成 SHA256 哈希（用于 content_hash 唯一约束）"""
    return hashlib.sha256(f"{title}:{url}".encode()).hexdigest()


def normalize_url(url: str) -> str:
    """URL 规范化：去除 fragment、统一 scheme、去除末尾斜杠。

    保留 query 参数（可能用于跟踪或去重）。
    """
    parsed = urlparse(url)
    path = parsed.path.rstrip("/") if parsed.path != "/" else ""
    if not path:
        path = ""
    cleaned = f"{parsed.scheme}://{parsed.netloc.lower()}{path}"
    if parsed.query:
        cleaned += "?" + parsed.query
    return cleaned


def ensure_timezone(dt: Optional[datetime]) -> Optional[datetime]:
    """确保 datetime 有时区信息，不支持的设为当前 UTC。

    如果解析出的时间在未来（超过 1 小时偏差），说明源时间戳
    （如 RSS pubDate）可能因无时区信息导致解析偏差，
    回退到当前 UTC 时间，避免前端显示未来时间。
    """
    if dt is None:
        return datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    # 超过 1 小时的未来时间 → 源时间戳偏差，回退到当前时间
    now = datetime.now(timezone.utc)
    if dt > now:
        return now
    return dt


def html_to_text(html: str | None) -> str | None:
    """简单的 HTML 到纯文本转换，用于 content_raw"""
    if not html:
        return None
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "lxml")
    text = soup.get_text(separator="\n", strip=True)
    # 合并多余空行
    return re.sub(r"\n{3,}", "\n\n", text)
