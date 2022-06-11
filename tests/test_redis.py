import pytest


@pytest.mark.usefixtures('redis_manager_connect')
@pytest.mark.asyncio
async def test_reader(redis_manager):
    await redis_manager.publish_message('test_user', 'test_message')

    message_data = await redis_manager.reader()
    assert message_data == {'sender': 'test_user', 'message': 'test_message'}


@pytest.mark.usefixtures('redis_manager_save_message')
@pytest.mark.asyncio
async def test_get_last_messages(redis_manager):
    messages = await redis_manager.get_last_messages()
    assert messages == ['<test_user>: test_message']
