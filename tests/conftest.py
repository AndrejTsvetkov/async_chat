# pylint: disable=W0621
import fakeredis.aioredis
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

from app.main import app
from app.redis import RedisManager


@pytest.fixture()
def redis_mock(mocker):
    return mocker.patch('app.routers.chat.redis_manager', autospec=True)


@pytest.fixture()
def redis_history_mock(mocker):
    return mocker.patch.object(RedisManager, 'get_last_messages', autospec=True)


@pytest.fixture()
def redis_reader_mock(redis_mock):
    redis_mock.reader.return_value = {
        'sender': 'test_user',
        'message': 'test_message',
    }


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture()
def redis():
    return fakeredis.aioredis.FakeRedis(decode_responses=True)


@pytest.fixture()
def redis_manager(redis):
    return RedisManager(redis)


@pytest_asyncio.fixture()
async def redis_manager_connect(redis_manager):
    await redis_manager.connect()


@pytest_asyncio.fixture()
async def redis_manager_save_message(redis_manager):
    await redis_manager.save_message('test_user', 'test_message')
