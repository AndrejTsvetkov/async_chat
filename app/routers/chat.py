from typing import Any

from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates

from app.config import basedir
from app.connection import connection_manager
from app.redis import redis_manager
from app.schemas import History

router = APIRouter()


templates = Jinja2Templates(directory=basedir / 'app' / 'templates')


@router.on_event('startup')
async def connect_redis() -> None:  # noqa: F811
    await redis_manager.connect()


@router.on_event('shutdown')
async def disconnect_redis() -> None:  # noqa: F811
    await redis_manager.disconnect()


@router.get('/')
def get_home(request: Request) -> Any:  # pragma: no cover (rendering template)
    return templates.TemplateResponse('home.html', {'request': request})


@router.get('/chat')
def get_chat(request: Request) -> Any:  # pragma: no cover (rendering template)
    return templates.TemplateResponse('chat.html', {'request': request})


@router.get(
    '/history',
    response_model=History,
)
async def get_history() -> History:
    last_messages = await redis_manager.get_last_messages()
    return History(messages=last_messages)


@router.websocket('/ws/{user_name}')
async def chat(websocket: WebSocket, user_name: str) -> None:
    # manager
    await connection_manager.connect(websocket)

    # redis
    await redis_manager.publish_message(user_name, 'got connected!')

    try:
        while True:
            # read new message from redis
            message_data = await redis_manager.reader()
            # send this message to all connected users
            await connection_manager.broadcast(message_data)
            # save in history
            await redis_manager.save_message(
                message_data['sender'], message_data['message']
            )

            # receive any new message from this user (front)
            data = await websocket.receive_json()

            # publish the new message to redis
            await redis_manager.publish_message(data['sender'], data['message'])

    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)

        message_data = {
            'sender': user_name,
            'message': 'left our chat :(',
        }
        await redis_manager.publish_message(
            message_data['sender'], message_data['message']
        )
        await redis_manager.save_message(
            message_data['sender'], message_data['message']
        )
        await connection_manager.broadcast(message_data)
