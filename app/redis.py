import asyncio

import aioredis
import async_timeout

from app.config import get_settings


def init_redis() -> aioredis.Redis:
    return aioredis.Redis.from_url(url=get_settings().REDIS_URL, decode_responses=True)


class RedisManager:
    def __init__(self, redis_interface: aioredis.Redis):
        self.redis = redis_interface
        self.pubsub = self.redis.pubsub()

        self.common_room_channel = get_settings().COMMON_ROOM_CHANNEL
        # for history
        self.history_list = get_settings().HISTORY_LIST_KEY
        self.history_list_size = get_settings().HISTORY_LIST_SIZE - 1

    async def connect(self) -> None:
        await self.pubsub.subscribe(self.common_room_channel)

    async def disconnect(self) -> None:
        await self.pubsub.unsubscribe(self.common_room_channel)

    async def reader(self) -> dict[str, str]:
        while True:
            try:
                async with async_timeout.timeout(1):
                    message = await self.pubsub.get_message(
                        ignore_subscribe_messages=True
                    )
                    if message is not None:
                        user_name, user_message = self.get_split_message_data(
                            message['data']
                        )
                        return {
                            'sender': user_name,
                            'message': user_message,
                        }
                await asyncio.sleep(0.01)
            except asyncio.TimeoutError:
                pass

    async def publish_message(self, user_name: str, message: str) -> None:
        signed_message = self.get_signed_message(user_name, message)
        await self.redis.publish(self.common_room_channel, signed_message)

    async def save_message(self, user_name: str, message: str) -> None:
        signed_message = f'<{user_name}>: {message}'
        await self.redis.lpush(self.history_list, signed_message)
        await self.redis.ltrim(self.history_list, 0, self.history_list_size)

    async def get_last_messages(self) -> list[str]:
        return await self.redis.lrange(self.history_list, 0, -1)

    @staticmethod
    def get_signed_message(user_name: str, message: str) -> str:
        return f'{user_name}:{message}'

    @staticmethod
    def get_split_message_data(message_data: str) -> list[str]:
        return message_data.split(':', 1)


redis = init_redis()
redis_manager = RedisManager(redis)
