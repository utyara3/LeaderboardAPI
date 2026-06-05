from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from redis.asyncio import Redis
from src.core.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, redis: Redis):
        super().__init__(app)
        self.redis = redis

    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith(("/static", "/docs", "/openapi.json")):
            return await call_next(request)

        client_id = request.client.host

        limit, window = self._get_limit_for_path(request.url.path, request.method)

        key = f"ratelimit:{client_id}:{request.method}:{request.url.path}"

        current = await self.redis.get(key)

        if current and int(current) >= limit:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": f"Rate limit exceeded. Try again in {window} seconds.",
                    "retry_after": window,
                },
            )

        async with self.redis.pipeline() as pipe:
            await pipe.incr(key)
            await pipe.expire(key, window)
            await pipe.execute()

        response = await call_next(request)
        return response

    def _get_limit_for_path(self, path: str, method: str) -> tuple[int, int]:
        if path.startswith("/auth/login") or path.startswith("/auth/register"):
            return settings.RATE_LIMIT_AUTH_REQUESTS, settings.RATE_LIMIT_WINDOW_SECONDS

        if "/submit" in path:
            return (
                settings.RATE_LIMIT_SUBMIT_REQUESTS,
                settings.RATE_LIMIT_WINDOW_SECONDS,
            )

        if path.startswith("/leaderboards"):
            return settings.RATE_LIMIT_API_REQUESTS, settings.RATE_LIMIT_WINDOW_SECONDS

        return settings.RATE_LIMIT_DEFAULT_REQUESTS, settings.RATE_LIMIT_WINDOW_SECONDS
