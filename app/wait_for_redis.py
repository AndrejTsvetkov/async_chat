import asyncio
import time

from aioredis import Redis
from aioredis.exceptions import ConnectionError as RedisConnectionError

from app.config import get_settings


async def wait_for_redis() -> None:  # pragma: no cover
    print('Waiting for redis...')
    redis_up = False
    while redis_up is False:
        try:
            redis = Redis.from_url(get_settings().REDIS_URL)
            await redis.ping()
            redis_up = True
        except RedisConnectionError:
            print('Redis unavailable, waiting 1 second...')
            time.sleep(1)

    print('Redis ready!')


if __name__ == '__main__':  # pragma: no cover
    asyncio.run(wait_for_redis())
