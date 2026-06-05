from redis.asyncio import Redis
from src.core.config import settings

redis = Redis.from_url(
    url=settings.REDIS_URL,
    decode_responses=True,
    socket_connect_timeout=5,
)


async def get_redis() -> Redis:
    return redis
