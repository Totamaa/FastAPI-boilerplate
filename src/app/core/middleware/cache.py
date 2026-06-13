from hashlib import md5

from fastapi import Request
from starlette.responses import Response as StarletteResponse


async def etag_middleware(request: Request, call_next):
    response = await call_next(request)

    if request.method not in ("GET", "HEAD") or response.status_code != 200:
        return response

    chunks: list[bytes] = []
    async for chunk in response.body_iterator:
        chunks.append(chunk if isinstance(chunk, bytes) else chunk.encode())
    body = b"".join(chunks)
    etag = f'"{md5(body).hexdigest()}"'  # noqa: S324

    if request.headers.get("If-None-Match") == etag:
        return StarletteResponse(
            status_code=304,
            headers={
                "ETag": etag,
                "Cache-Control": response.headers.get("Cache-Control", ""),
            },
        )

    new_response = StarletteResponse(
        content=body,
        status_code=response.status_code,
        media_type=response.media_type,
    )
    for key, value in response.headers.items():
        if key.lower() not in ("content-length", "transfer-encoding"):
            new_response.headers[key] = value
    new_response.headers["ETag"] = etag
    return new_response
