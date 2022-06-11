import pytest


def test_get_history(client, redis_history_mock):
    redis_history_mock.return_value = ['<test_user>: test_message']
    response = client.get('/history')

    assert response.status_code == 200
    data = response.json()
    assert data['messages'] == ['<test_user>: test_message']


@pytest.mark.usefixtures('redis_reader_mock')
def test_websocket_connect(client):
    with client.websocket_connect('/ws/test_user') as websocket:
        data = websocket.receive_json()
    assert data == {
        'sender': 'test_user',
        'message': 'test_message',
    }
