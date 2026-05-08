from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from httpx import AsyncClient
from urllib.parse import urlparse

router = APIRouter(prefix="/api/images", tags=["images"])


@router.get("/proxy")
async def proxy_image(url: str = Query(..., description="External image URL to proxy")):
    """代理外部图片，避免防盗链和跨域问题。

    使用 httpx 流式传输外部图片内容，支持重定向。
    仅允许 http/https scheme。返回图片内容并设置 24 小时缓存。
    """
    # 安全校验：只允许 http/https
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise HTTPException(status_code=400, detail="Only http/https URLs allowed")

    try:
        async with AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, follow_redirects=True)
            resp.raise_for_status()
            content_type = resp.headers.get("content-type", "")
            if not content_type.startswith("image/"):
                raise HTTPException(
                    status_code=400, detail="URL does not point to an image"
                )
            return StreamingResponse(
                resp.aiter_bytes(),
                media_type=content_type,
                headers={
                    "Cache-Control": "public, max-age=86400",
                    "X-Image-Source": url,
                },
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=502, detail=f"Failed to fetch image: {str(e)}"
        )
